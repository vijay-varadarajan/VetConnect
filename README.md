# VETCONNECT
### by Vijay Varadarajan 
### with **KeshavKartha**, **Gaurav** and **Ayush**

### from TamilNadu, India
#### Video Demo:  <URL HERE>
#### Github repo link: [VetConnect-Source_code](https://github.com/vijay-varadarajan/VetConnect)
## About this project
This is a web application that is made to promote veterinary healthcare and pet health in India. This primarily allows any user to submit a report about a stray or injured animal and the user receives a list of nearby veterinary hospitals/clinics with contact details and directions.

Legitimate veterinary hospitals with valid authentication IDs can add their hospital names to the databese through the same website.

In addition to this, the user can sign up and store details of their pet(s) in the database and can access and modify it anytime they want. This allows users to keep track of their pet's needs and cater to the same.

## Features

+ Allows quick reporting without needing to login.

+ Sorts nearby veterinary clinics/hospitals based on the type of pet and distance.

+ Displays names, contact details and map location of veterinary clinics nearby.

+ The authentication ID of hospitals is checked while adding.

+ Uses the Haversine formula to calculate the distance between two locations.

+ Lets users signup to store details of his/her pet(s).

+ Stores users passwords in encrypted form.

+ Lets users reset thier passwords if forgotten.

+ Gives each user their own table to store pet(s) details.

+ Lets users modify / delete the added details.

+ Checks for invalid data at all input fields and works accordingly.

## Working

1. The homepage of this website has buttons to take the user to 'login', 'register', 'report' and 'add hospital' pages.

2. The report section requires the user to fill a form with the details of their location and the trivial details of the animal that the user wants to report about. 

3. After submitting the report, the user sees a table that lists the veterinary hospitals/clinics nearby along with contact details and link to maps that takes the user to google maps, for the directions to that place and a web link to the website of that place.

4. From the homepage, the user can also add their hospital details through the 'add your hospital' link, provided their hospital is a legitimate veterinary centre. This is confirmed with the authentication ID, that is unique to this website.

5. The register page requires the user to create a new unique username and password to register, for storing their pet(s) info. 

6. The login page requires the user to login with the registerd username and password. It also allows the user to reset their password if forgotten, through the 'Forgot password' link.

7. The 'Forgot password' link asks the user for their username, mail ID and phone number which is checked against the database and if legit, the old hashed password is replaced with the new hashed password.

8. After logging in / registering, the user can add details of his or her pets by clicking on 'Add', such as: the name, age, weight, vaccination status and additional info if needed.

9. The user's homepage, as soon as they login, displays the stored details of the pets.

10. These details can be modified through 'Modify' where the user needs to fill only the columns that need to be updated. 

11. A pet can be removed through 'Remove' where the user needs to specify the name of the pet to remove.

## Implementation details

<b> Framework used: </b> Flask

<details>

<summary><b>Python libraries used</b></summary>

 - math
 - functools
 - werkzeug.security
 - geopy
 - cs50
 - flask
 - flask_session

</details>


