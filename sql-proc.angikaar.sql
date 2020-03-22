
delimiter //
drop procedure if exists `ProcessConversation`
//

CREATE PROCEDURE ProcessConversation()
BEGIN
   -- Declare local variables
   
   DECLARE done BOOLEAN;
   DECLARE tmpsender varchar(200);
   declare currentId INT;
   Declare oldSender varchar(200) default 'none';
   DECLARE tmpmessage text;
   declare allmsg text default '';
   DECLARE tmptimestamp datetime(6);
   declare lastupdated INT;
   -- Declare the cursor
   DECLARE chattexts CURSOR
   FOR
   SELECT id,sender,message,timestamp FROM chat_text;
   -- Declare continue handler
   
   DECLARE CONTINUE HANDLER FOR SQLSTATE '02000' SET done=1;
   set done=0;
  select lastid into lastupdated from last_merge limit 1;
  select lastupdated ;
   -- Create a table to store the results
  CREATE TABLE IF NOT EXISTS conversation_consolidation
      (sender varchar(200), msg varchar(10000), timestamp datetime(6));
   -- Open the cursor
	
   OPEN chattexts;
   -- Loop through all rows
   FETCH chattexts INTO currentId,tmpsender,tmpmessage,tmptimestamp;
   set allmsg=tmpmessage;
   
   REPEAT
  	
      IF oldSender <> tmpsender and currentId > lastupdated then
	set oldSender=tmpsender;
      -- Insert order and total into ordertotals
      INSERT INTO conversation_consolidation(sender,msg,timestamp)
	 VALUES(tmpsender,allmsg,tmptimestamp);
	set allmsg='';
     end if;
 -- Get order number
      FETCH chattexts INTO currentId,tmpsender,tmpmessage,tmptimestamp;
   IF oldSender = tmpsender then
	set allmsg=concat(allmsg,tmpmessage);
   else 
	set allmsg=tmpmessage;
     end if;
   -- End of loop
   UNTIL done END REPEAT;
   update last_merge set lastid=currentId;
   -- Close the cursor
   CLOSE chattexts;
END

//
delete from conversation_consolidation;   
update last_merge set lastid = 1; 
call ProcessConversation();

select * from conversation_consolidation;   
