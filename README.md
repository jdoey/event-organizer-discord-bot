# event-organizer-discord-bot
A Discord bot that assists users in a discord in organizing and planning events. Once an event is added, the bot will send an embedded message with the name, date, time, and point of contact of the event. The bot will also add reactions to the embedded messages so that users in the discord can react to the message to show whether or not they can attend the event. The bot will also create a dedicated text channel and role just for the event to make planning easier. Should the event details change, the user can update the details of the event by simply calling the ;changeevent command and inputting what they wish to change. If minds change, users can delete any event by calling the ;deleteevent command and inputting the event name and the event ID that is located in the contents of the embedded message. This bot utilizes a MongoDB database to store the embedded message IDs which also contains the role ID and text channel ID that is linked to the embedded message. Users who react with a ✅ or ❔ are automatically given a role that corresponds with the event and are thus given access to the text channel created for the event.

Created using: Python and MongoDB

Deployed using: Repl.it and UptimeRobot

![image](https://user-images.githubusercontent.com/70018021/127807801-32fb2e8d-f472-40f4-a85b-d67a596f9665.png)




**commands:**

**;setembedchannel**
    -prompts user who called command to enter:
    
    
    
    the channel id of the channel they wish to send the embedded message:
    
    -sets the channel in which the embedded messages will be sent by the bot
    -writes the channel ID into a JSON file and reads it
    
**;addevent**
  -prompts user who called command to enter:
  
  
  
    name of event:
    date of event:
    time of event:
    point of contact:
    
    -the command will create and send an embedded message with the details above in a specified channel.
    -it will also create a corresponding text channel and role with the proper permissions.
    -the message ID, role ID, and text channel ID of the event will be stored into a MongoDB database.
    
**;deleteevent("event name", unique_5_character_embedded_message_code)**
  
  
     -deletes the specified event message as well as its corresponding text channel and role.
     -deletes the data entry of the message from the database.
  
**;changeevent(unique_5_character_embedded_message_code)**


     -allows the user to edit the embedded message's event name.
     -changes the text channel name and role name to correspond with the new event name.
     
**;changedesc(unique_5_character_embedded_message_code)**

     -allows the user to edit the embedded message's event description.
     
**;changedate(unique_5_character_embedded_message_code)**

     -allows the user to edit the embedded message's event date.
     
**;changetime(unique_5_character_embedded_message_code)**

     -allows the user to edit the embedded message's event time. 
     
**;changepoc(unique_5_character_embedded_message_code)**

     -allows the user to edit the embedded message's point of contact.  
    
  
**events:**

 **on_raw_reaction_add**
  
  
    -assigns the user that reacts with a checkmark to the message with a role that corresponds to the event.
    -prevents the user from reacting to more than one emoji in a given embedded message.
    
 **on_raw_reaction_remove**
 
    -removes the corresponding role from the user when the checkmark reaction or question mark reaction is removed.
    
 **anti_spam**
    
    -automatically removes messages from the events channel that are not sent by the bot.
    -prevents users from clogging up the channel with messages that do not pertain to the event.
  
