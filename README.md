# event-organizer-discord-bot
A Discord bot that assists users in a discord in organizing and planning events





**commands:**

**;setembedchannel**
    -prompts user who called command to enter:
    
    
    
    the channel id of the channel they wish to send the embedded message:
    
    -sets the channel in which the embedded messages will be sent by the bot
    
**;addevent**
  -prompts user who called command to enter:
  
  
  
    name of event:
    date of event:
    time of event:
    
    -the command will create and send an embedded message with the details above in a specified channel.
    -it will also create a corresponding text channel and role.
    
**;deleteevent(unique_5_character_embedded_message_code, "event name")**
  
  
     -deletes the specified event message as well as its corresponding text channel and role.
  
**;changeevent("new event name", new_event_date, new_event_time, unique_5_character_embedded_message_code)**


     -edits the embedded message with the details in the arguments.
  
**events:**

 **on_raw_reaction_add**
  
  
    -assigns the user that reacts with a checkmark to the message with a role that corresponds to the event
    -prevents the user from reacting to more than one emoji in a given message
    
 **on_raw_reaction_remove**
 
    -removes the corresponding role from the user when the checkmark reaction is removed
    
 **anti_spam**
    
    -automatically removes messages from the events channel that are not sent by the bot
  
