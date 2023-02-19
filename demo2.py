def mixedform_demo(): 
         HIDDEN    = 0x1 
         READ_ONLY = 0x2 
  
         elements = [ 
             ("Size (cm)", 1, 1, "175", 1, 20, 4, 3, 0x0), ("Weight (kg)", 2, 1, "85", 2, 20, 4, 3, 0x0), ("City", 3, 1, "Groboule-les-Bains", 3, 20, 15, 25, 0x0), ("State", 4, 1, "Some Lost Place", 4, 20, 15, 25, 0x0), ("Country", 5, 1, "Nowhereland", 5, 20, 15, 20, 0x0), (r"\/3r`/ 53kri7 (0d3", 11, 1, "", 11, 20, 15, 20, HIDDEN) ] 
  
         code, fields = d.mixedform( 
             "Please fill in some personal information:", elements, width=77) 
  
         return fields


mixedform_demo()
