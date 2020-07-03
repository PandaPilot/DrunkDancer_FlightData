# DrunkDancer_FlightData

1. Save rosbag file into this directory
2. run "  python bag_to_csv.py  "

rosbag will be moved to new directory with raw data Flight_Data.csv and processed data Processed.csv

3. running " python recover_bag.py " will delete the work done by bag_to_csv and return all the bag files to original location
