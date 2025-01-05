import argparse
import aiopioneer
import asyncio
import os

from aiopioneer.const import Zone

parser = argparse.ArgumentParser(description='hdzone-mirror - automatic mirroring of the current digital source to the HDZone for Pioneer receivers')
parser.add_argument('ip', type=str, help='AV IP address')
parser.add_argument('mirrored_sources_path', type=str, help='Path to the text file containing the sources which should be mirrored to the HDZone')
args = parser.parse_args()

if not os.path.exists(args.mirrored_sources_path):
    raise FileNotFoundError("Cannot find mirrored sources text file")

try:
    with open(args.mirrored_sources_path, "rt") as reader:
        mirrored_sources = reader.read().split("\n")
        mirrored_sources = [ source.strip() for source in mirrored_sources ]
except:
    raise Exception("Could not open mirrored sources text file")

vsx = aiopioneer.PioneerAVR(args.ip)

async def connect_to_receiver():
    while True:
        try:
            # print(f"Attempting to connect to receiver ..")
            await vsx.connect(reconnect=False)
            print("Connected to the receiver!")
            # Go down once connected
        except Exception as e:
            # print(f"Failed to connect: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue # Restart loop from the beginning, which means we end up trying to connect again
    
        while True:
            try:
                # print("Query zones")
                await asyncio.wait_for(vsx.query_zones(), timeout=20)
                # print("Update")
                await asyncio.wait_for(vsx.update(), timeout=40)
                # print("Build source dict")
                await asyncio.wait_for(vsx.build_source_dict(), timeout=20)
                # print("Sleep")
                await asyncio.sleep(1)

                # print(vsx.properties.power)
                # print(vsx.properties.source_name)

                # If main zone is active
                if vsx.properties.power[Zone.Z1]:
                    current_main_source_id = vsx.properties.source_name[Zone.Z1]
                    current_main_source = vsx.properties.get_source_name(current_main_source_id)

                    # print(current_main_source)

                    # If the current source is one that should be mirrored
                    if current_main_source in mirrored_sources:
                        # If HDZone is not on, turn it on
                        if not vsx.properties.power[Zone.HDZ]:
                            print("HDZone should be turned on for this source")
                            print("Turning on HDZone...")
                            await vsx.turn_on(Zone.HDZ)
                            await asyncio.sleep(1)
                            continue # We need to re-query for source info for HDZone!

                        # If HDZone source is not the same as the main source, set it
                        if vsx.properties.source_name[Zone.HDZ] != current_main_source_id:
                            print("HDZone source should be mirrored from main source")
                            print("Mirroring source...")
                            await vsx.select_source(source=current_main_source, zone=Zone.HDZ)
                    # If current source is not one that should be mirrored, and HDZone is on, turn it off
                    elif vsx.properties.power[Zone.HDZ]:
                        print("No mirroring is necessary, but HDZone is still on")
                        print("Turning off HDZone...")
                        await vsx.turn_off(Zone.HDZ)

                # If main is not active but HDZone is, turn it off
                elif not vsx.properties.power[Zone.Z1] and vsx.properties.power[Zone.HDZ]:
                    print("Main zone is turned off, but HDZone is still on")
                    print("Turning off HDZone...")
                    await vsx.turn_off(Zone.HDZ)
            except:
                print("Receiver command failed. Receiver probably went offline.")
                print("Returning to connection loop...")
                await vsx.disconnect()
                break

            # print("Sleep 5 seconds (internal)")
            await asyncio.sleep(5)

        print("Sleep 5 seconds after fail")
        await asyncio.sleep(5)
    
    await vsx.disconnect()

if __name__ == "__main__":
    asyncio.run(connect_to_receiver())
