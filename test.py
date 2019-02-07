import json
schedule=json.loads(open("schedule/schedule.json","r").read())
schedule_day=json.loads(open("schedule/day/0.json","r").read())
for day in range(0, len(schedule['days'])):
      print("[O] Adding day "+str(day))
      print("Day %d of %d: %s"% (day+1, len(schedule['days']), schedule["days"][str(day)]))

room_selected=0
room_list=[]
for room in schedule_day["rooms"]:
    room_list.append(room)
print(room_list)
for x in range(0,3):
    for event in schedule_day["rooms"][room_list[room_selected+x]]:
            #convert time from hh:mm to minutes
            event_start      = event["start"].split(":")
            event_start_mins = 60*int(event_start[0])+int(event_start[1])
            if event_start[0] == "00":
                #assume it's late at night
                event_start_mins = 24*60


            event_duration   = event["duration"].split(":")
            event_dur_mins   = 60*int(event_duration[0])+int(event_duration[1])

            event_stop_mins  = event_start_mins + event_dur_mins 

            event_end_hour, event_end_min = divmod(event_stop_mins, 60)

            event_time = event["start"] + " - " + str(event_end_hour) + ":" + str(event_end_min)
            if event_end_min == 0:
                event_time = event_time + "0"

            print("Event: "+room_list[room_selected+x]+" title: "+event["title"]+" start: "+str(event_start_mins) + " stop: "+str(event_stop_mins))

