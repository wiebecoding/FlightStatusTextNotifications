#Python program that gets user flight information from FlightAware API and texts such information using Twillo
import json
import requests
import config

from datetime import datetime
from twilio.rest import Client 

#transformation between common airline name to ICAO name
def AlaskaAirlines():
    return "ASA"
def AllegiantAir():
    return "AAY"
def AmericanAirlines():
    return "AAL"
def DeltaAirLines():
    return "DAL"
def FrontierAirlines():
    return "FFT"
def HawaiianAirlines():
    return "HAL"
def JetBlue():
    return "JBU"
def SouthwestAirlines():
    return "SWA"
def SpiritAirlines():
    return "NKS"
def UnitedAirlines():
    return "UAL"

nameToICAO = {
    'united': UnitedAirlines,
    'spirit': SpiritAirlines,
    'southwest': SouthwestAirlines,
    'jetblue': JetBlue,
    'hawaiian': HawaiianAirlines,
    'frontier': FrontierAirlines,
    'delta': DeltaAirLines,
    'american': AmericanAirlines,
    'allegiant': AllegiantAir,
    'alaska': AlaskaAirlines
}

#user request of airline and ICAO tranformation
def get_airline():
    airline = input("What airline are you flying?:\n> ")
    airline = airline.lower()
    ICAO = nameToICAO.get(airline)()
    if ICAO == None:
        return get_airline()
    else:
        return ICAO

#user request for flight number
def get_info():
    code = get_airline()
    flightNum = input("What is the flight number?:\n> ")
    return code + flightNum

#using user input, send query to server, returns plain text of flight info
def query_server(ident):
    payload = {'max_pages': 1}
    auth_header = {'x-apikey': config.apiKey}
    apiURL = "https://aeroapi.flightaware.com/aeroapi/flights/" + ident

    response = requests.get(apiURL,params=payload,headers=auth_header)
    if response.status_code == 200:
        return response.text
    else:
        print("Information could not be found on that flight. Try agian later")
        quit()

#creates message for text and prints
def show_data(info):
    info = json.loads(info)
    output = ''
    data = info.get("flights")
    today = datetime.now()
    date = int(today.strftime("%d"))
    hour = int(today.strftime("%H"))
    for i in range(len(data)):
        entireFlight = data[i]
        dateEntireFlight = entireFlight.get("scheduled_off")
        hourFlight = int(dateEntireFlight[11]+dateEntireFlight[12])
        if hourFlight < hour:
            dateFlight = int(dateEntireFlight[8]+dateEntireFlight[9])
            dateFlight -= 1
        else:
            dateFlight = int(dateEntireFlight[8]+dateEntireFlight[9])
        if date >= dateFlight:
            data = data[i]
            break
    identTxt = data.get("operator") + ' ' + data.get("flight_number")
    output += identTxt + '\n' + "-----------" + "\n"
    origin = data.get("origin")
    dest = data.get("destination")
    pathTxt = origin.get("code") + " ----> " + dest.get("code")
    output += pathTxt + "\n"
    status = data.get("status")
    if status != None:
        output += status + "\n"
    if data.get("departure_delay") == 0:
        delayed = "No"
        output += "Delayed: " + delayed + "\n"
    else:
        delayed = "Yes"
        output += "Delayed: " + delayed + "\n"
    if data.get("cancelled") == False:
        delayed = "No"
        output += "Cancelled: " + delayed + "\n"
    else:
        delayed = "Yes"
        output += "Cancelled: " + delayed + "\n"
    out = data.get("scheduled_out")
    out = datetime.fromisoformat(out.rstrip(out[-1]))
    output += "Scheduled Departure: " + str(out) + "\n"
    inT = data.get("scheduled_in")
    inT = str(datetime.fromisoformat(inT.rstrip(inT[-1])))
    output += "Scheduled Arrival: " + str(inT) + "\n"
    percent = data.get("progress_percent")
    if percent != None:
        output += "Progress Percent: " + str(percent) + "\n"
    print("The following message was sent:\n")
    print(output)
    return output

#sends message using Twillo
def send_data(info):
    client = Client(config.account_sid, config.auth_token) 
    
    message = client.messages.create(  
        messaging_service_sid=config.messaging_service_sid, 
        body= info,      
        to=config.number 
    )

#call outline in general
def main():
    ident = get_info()
    info = query_server(ident)
    out = show_data(info)
    send_data(out)

main()