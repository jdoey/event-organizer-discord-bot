# event-organizor-discord-bot
assists users in a discord organize events/plans

**commands:**

**;addevent**
  -prompts user who called command to enter:
  
  
  
    name of event:
    date of event:
    time of event:
    
    -the command will create and send an embedded message with the details above in a specified channel.
    -it will also create a corresponding text channel and role.
    
**;deleteevent(unique_5_character_embedded_message_code, "name of the event")**
  -deletes the specified event message as well as its corresponding text channel and role.
  
**;changeevent("name of the event", date_of_event, time_of_event, unique_5_character_embedded_message_code)**
  -edits the embedded message with the details in the arguments.
  
  
  
