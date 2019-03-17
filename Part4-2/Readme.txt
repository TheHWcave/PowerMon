Updates to Powermon source code after investigation into Ansmann Energy8+ charger. 
- fixing a problem in Recording.py when recording changes only. When plotting recordings,
  the previous code would lead to sloped lines instead of horizonal lines. 
- fixing a problem with autorange. A sudden increase in current would force an autorange 
  up and a range change command to the INA219 chip but then the code would continue to
  use the out-of-range measurement for display and recording instead of waiting for a 
  new measurement from the INA219 with the new range applied. 
- some small changes in Powermon.py to simplify how the loop counter is setup and when the 
  display is called.
