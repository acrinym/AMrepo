# Wildfire App List

#### You:
Please remove extrenous data, I only need the name of the applications in a list, please. 

Acronyms are fine, like IROC, Sit 2/09, E-Isuite, etc. 


Wildland fire applications
Filter
Filter tiles
Data Warehouse
Data Warehouse
DRONESIM
UAS Training, Flight Simulator

FEMS
Fire Environment Mapping System
FEPP FEPMIS
Federal Excess Personal Property Federal Excess Property Management Information System

FireCode
FireCode System

FireScience
Joint Fire Science Program

Flight
Flight

FMSF API
Fire Modeling Services Framework
FRx
Fire Reporting ("Stabilized" Module of WFMI)
FTP
F&AM FTP Onboarding

IFTDSS/FTEM
Interagency Fuel Treatment Decision Support System/Fuel Treatment Effectiveness Monitoring
IgPoint
Fire Ignition Points Website

IQCS
Incident Qualifications and Certification System

LESO FEPMIS
Law Enforcement Support Office Federal Excess Property Management Information System
NIFCSSO
NIFC Single Sign-On
NIROPS
National Infrared Operations Website

NPSG
National 7-Day Significant Fire Potential

OIS
Organization Information System
OLMS
Operational Loads Monitoring System

ROAD
Real-time Operations and Applications Dashboard
SAWTI
Santa Ana Wildfire Threat Index
SIT-209
National Interagency Situation Reporting System

Unit ID
Unit Identifier System

WFAIP-CM
Wildland Fire Application Information Portal - Content Management

WFDSSNG
Wildland Fire Decision Support System NextGen

WFMRDA
Wildland Fire Management Research and Development

WildCAD-E
WildCAD-E

WXx
Weather  ("Stabilized" Module of WFMI)

#### ChatGPT:
Here is the list of wildland fire applications with acronyms:

1. Filter

2. Filter tiles

3. Data Warehouse

4. DRONESIM

5. UAS Training

6. FEMS

7. FEPP FEPMIS

8. FireCode

9. FireScience

10. Flight

11. FMSF API

12. FRx

13. FTP

14. IFTDSS/FTEM

15. IgPoint

16. IQCS

17. LESO FEPMIS

18. NIFCSSO

19. NIROPS

20. NPSG

21. OIS

22. OLMS

23. ROAD

24. SAWTI

25. SIT-209

26. Unit ID

27. WFAIP-CM

28. WFDSSNG

29. WFMRDA

30. WildCAD-E

31. WXxHere is the list of wildland fire applications with acronyms:

32. Filter

33. Filter tiles

34. Data Warehouse

35. DRONESIM

36. UAS Training

37. FEMS

38. FEPP FEPMIS

39. FireCode

40. FireScience

41. Flight

42. FMSF API

43. FRx

44. FTP

45. IFTDSS/FTEM

46. IgPoint

47. IQCS

48. LESO FEPMIS

49. NIFCSSO

50. NIROPS

51. NPSG

52. OIS

53. OLMS

54. ROAD

55. SAWTI

56. SIT-209

57. Unit ID

58. WFAIP-CM

59. WFDSSNG

60. WFMRDA

61. WildCAD-E

62. WXx


#### You:
So I want to create a Microsoft form to output prewritten tickets. 

Can I gather data on application requested, and then have MS forms write something like: 

"
Vendor Name (if applicable):
Current call back number: 	
Current email address:
FAMAuth Username: 
FAMAuth Account Status (Active, Disabled, or Removed): 
Email on FAMAuth Account:
Application Needed: 
On active incident (Y/N)?
User requested x application: 

#### ChatGPT:
Yes, you can definitely set up a Microsoft Form to gather data and then use it to output prewritten tickets. Here’s a step-by-step guide on how you can create such a form and automate the output:

### Step 1: Create the Microsoft Form

1. **Open Microsoft Forms**: Go to the Microsoft Forms website or access it through Office 365.
2. **Create a New Form**: Click on "New Form."
3. **Add Questions**:
   - **Vendor Name** (if applicable): Short Answer
   - **Current Call Back Number**: Short Answer
   - **Current Email Address**: Short Answer
   - **FAMAuth Username**: Short Answer
   - **FAMAuth Account Status**: Choice (Active, Disabled, Removed)
   - **Email on FAMAuth Account**: Short Answer
   - **Application Needed**: Choice (List all applications)
   - **On Active Incident?**: Choice (Yes/No)
   - **User Requested Application**: Choice (List all applications)

### Step 2: Automate the Ticket Generation

To automate the process of generating prewritten tickets, you can use Power Automate (formerly Microsoft Flow).

1. **Open Power Automate**: Go to the Power Automate website or access it through Office 365.
2. **Create a New Flow**: Click on "Create" and then select "Automated flow."
3. **Choose a Trigger**: Select the trigger "When a new response is submitted" for Microsoft Forms.
4. **Connect to Microsoft Forms**: Choose the form you created.
5. **Add an Action**: Add an action to "Get response details" from the form.
6. **Compose the Ticket**:
   - Add another action "Compose" and use the dynamic content from the form responses to create your prewritten ticket text. Your composition can look something like this:

```
Vendor Name (if applicable): @{triggerOutputs()?['body/YourQuestion1']}
Current call back number: @{triggerOutputs()?['body/YourQuestion2']}
Current email address: @{triggerOutputs()?['body/YourQuestion3']}
FAMAuth Username: @{triggerOutputs()?['body/YourQuestion4']}
FAMAuth Account Status (Active, Disabled, or Removed): @{triggerOutputs()?['body/YourQuestion5']}
Email on FAMAuth Account: @{triggerOutputs()?['body/YourQuestion6']}
Application Needed: @{triggerOutputs()?['body/YourQuestion7']}
On active incident (Y/N)? @{triggerOutputs()?['body/YourQuestion8']}
User requested @{triggerOutputs()?['body/YourQuestion9']} application:
```

### Step 3: Output the Ticket

You can choose how to output this composed ticket. Common methods include:

1. **Send an Email**: Add an action to "Send an email" with the composed text.
2. **Create a File**: Add an action to "Create file" in OneDrive or SharePoint with the ticket details.
3. **Post in Teams**: Add an action to "Post a message" in Microsoft Teams.

By following these steps, you can streamline the process of generating prewritten tickets based on the data collected through Microsoft Forms.


#### You:
Could Power automate juist output text for me? 

#### ChatGPT:
Yes, Power Automate can output text for you, which you can then use as needed. Here’s how you can set it up to output the composed text:

### Step 1: Create the Microsoft Form

1. **Open Microsoft Forms**: Go to the Microsoft Forms website or access it through Office 365.
2. **Create a New Form**: Click on "New Form."
3. **Add Questions**:
   - **Vendor Name** (if applicable): Short Answer
   - **Current Call Back Number**: Short Answer
   - **Current Email Address**: Short Answer
   - **FAMAuth Username**: Short Answer
   - **FAMAuth Account Status**: Choice (Active, Disabled, Removed)
   - **Email on FAMAuth Account**: Short Answer
   - **Application Needed**: Choice (List all applications)
   - **On Active Incident?**: Choice (Yes/No)
   - **User Requested Application**: Choice (List all applications)

### Step 2: Automate the Text Output

To automate the text output using Power Automate:

1. **Open Power Automate**: Go to the Power Automate website or access it through Office 365.
2. **Create a New Flow**: Click on "Create" and then select "Automated flow."
3. **Choose a Trigger**: Select the trigger "When a new response is submitted" for Microsoft Forms.
4. **Connect to Microsoft Forms**: Choose the form you created.
5. **Add an Action**: Add an action to "Get response details" from the form.
6. **Compose the Text**:
   - Add another action "Compose" and use the dynamic content from the form responses to create your prewritten ticket text. Your composition can look something like this:

```
Vendor Name (if applicable): @{outputs('Get_response_details')?['body/YourQuestion1']}
Current call back number: @{outputs('Get_response_details')?['body/YourQuestion2']}
Current email address: @{outputs('Get_response_details')?['body/YourQuestion3']}
FAMAuth Username: @{outputs('Get_response_details')?['body/YourQuestion4']}
FAMAuth Account Status (Active, Disabled, or Removed): @{outputs('Get_response_details')?['body/YourQuestion5']}
Email on FAMAuth Account: @{outputs('Get_response_details')?['body/YourQuestion6']}
Application Needed: @{outputs('Get_response_details')?['body/YourQuestion7']}
On active incident (Y/N)? @{outputs('Get_response_details')?['body/YourQuestion8']}
User requested @{outputs('Get_response_details')?['body/YourQuestion9']} application:
```

### Step 3: Output the Text

To simply output the composed text, you can use a "Send me a mobile notification" action or a "Post a message" action:

1. **Send a Mobile Notification**:
   - Add an action "Send me a mobile notification."
   - In the message content, add the dynamic content from the "Compose" action.
2. **Post a Message to Teams** (optional):
   - If you prefer to see the output in a Microsoft Teams channel, add an action "Post a message" in Teams with the dynamic content from the "Compose" action.

### Example Flow Summary

1. **Trigger**: When a new response is submitted.
2. **Action**: Get response details.
3. **Action**: Compose text.
4. **Action**: Send me a mobile notification (or Post a message to Teams).

By following these steps, you will be able to receive the composed text directly from Power Automate, making it easy for you to use the prewritten ticket information as needed.


#### You:
No, I just want the text there, under the questions, in Microsoft forms. Is that possible? I don't want a text or a teams post. 

#### ChatGPT:
Got it! If you want to display the prewritten ticket text directly within the Microsoft Form itself, you can add a section at the end of the form where the text is shown. However, note that Microsoft Forms does not have a built-in way to dynamically generate text based on form responses within the form itself.

You can manually add a section with the prewritten ticket format as a reference for users to fill in the required fields. Here's how you can do it:

### Step 1: Create the Microsoft Form

1. **Open Microsoft Forms**: Go to the Microsoft Forms website or access it through Office 365.
2. **Create a New Form**: Click on "New Form."
3. **Add Questions**:
   - **Vendor Name** (if applicable): Short Answer
   - **Current Call Back Number**: Short Answer
   - **Current Email Address**: Short Answer
   - **FAMAuth Username**: Short Answer
   - **FAMAuth Account Status**: Choice (Active, Disabled, Removed)
   - **Email on FAMAuth Account**: Short Answer
   - **Application Needed**: Choice (List all applications)
   - **On Active Incident?**: Choice (Yes/No)
   - **User Requested Application**: Choice (List all applications)

### Step 2: Add the Prewritten Ticket Text as a Reference

1. **Add a New Section**: Click on "Add New" and select "Section."
2. **Title the Section**: Name it something like "Prewritten Ticket Format."
3. **Add the Ticket Text**: In the description of the section, write out the prewritten ticket format. For example:

```
Vendor Name (if applicable): [Enter Vendor Name]
Current call back number: [Enter Call Back Number]
Current email address: [Enter Email Address]
FAMAuth Username: [Enter FAMAuth Username]
FAMAuth Account Status (Active, Disabled, or Removed): [Enter FAMAuth Account Status]
Email on FAMAuth Account: [Enter Email on FAMAuth Account]
Application Needed: [Enter Application Needed]
On active incident (Y/N)?: [Enter Yes or No]
User requested [Enter Application Needed] application:
```

### Example Layout

1. **Section 1: User Information**
   - Vendor Name (if applicable): Short Answer
   - Current Call Back Number: Short Answer
   - Current Email Address: Short Answer
   - FAMAuth Username: Short Answer
   - FAMAuth Account Status: Choice (Active, Disabled, Removed)
   - Email on FAMAuth Account: Short Answer
   - Application Needed: Choice (List all applications)
   - On Active Incident? (Y/N): Choice (Yes/No)
   - User Requested Application: Choice (List all applications)

2. **Section 2: Prewritten Ticket Format**
   - **Description**: Include the prewritten ticket text as shown above.

This approach allows you to display the format for the ticket directly within the form for users to reference as they fill out the fields. It ensures that all necessary information is gathered and can be copied and pasted into a ticket system if needed.
