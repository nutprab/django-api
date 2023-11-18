Repo for completing Django Api Project

Coursera - 

pipfile - python version 3.8

To activate pipenv shell
 1. Change path - export PATH="$PATH:$HOME/.local/bin"
 2. go to folder -  cd django-api-main/project-api/
 3. activate virtual environment -  pipenv shell
 4. install dependencies - pipenv install


After run server
 1. superuser creds
    a. username - admin
    b. password - admin@123
    c. Auth Token = 908a306dcdd77ba9c23f9809aff7ac48c1981253
 2. Managers
    a. email    - manager{#}@ll.com  [manager1@ll.com]
    b. username - manager{#}         [manager1]
    c. password - Deliver@{###}      [Delivery@001]
    d. Auth Token = be61070a52ff4f325d1f5072c9a1e6f6ab914782
 3. Delivery Crew
    a. email    - delcrew{#}@ll.com  [delcrew1@ll.com]
    b. username - delcrew{#}         [delcrew1]
    c. password - Manager@{###}      [Manager@001]
    d. Auth Token = fa6a81a154034d8d767be3c7fe7265cb74f9f03f
 4. Customer
    a. username - customer1
    b. password - AdminUser@001
    c. Auth Token = 4b68938462233723521abc13b9c6a5fc863d17f2


USAGE 

1. Cart
   a. GET 
      i. Auth Token
   b. POST
      i. Auth Token
      ii. Body Params
         1. menuitem_id = ID of menu item to be added to cart
         2. quantity    = Quantity of menu item
   c. DELETE
      i. Auth Token
      ii. Body Params
         1. menuitem_id = ID of menu item to be deleted
2. Order
