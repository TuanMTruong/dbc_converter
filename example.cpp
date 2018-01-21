#include <iostream>
#include <stdint.h>
#include "can_messages.hpp"


using namespace std;


int main(){

	// -------- Receiving a message --------
	// incoming message:
	uint32_t receiveID = 0x201;
	uint8_t receiveData[8] = {0xB8, 0x0B, 2, 0xA0, 0x41, 2, 0xC4, 0x09};

	// Moving message to container:
	if (receiveID == idTable::Vehicle_Status_id){
		cout << "Got Message." << endl;
		Vehicle_Status_Message VSMsg(receiveData);
		// prints out data in container:
		cout << (int)VSMsg.getRPM() << " rpm" << endl;
		cout << (int)VSMsg.getVoltage() << " mV" << endl;
		cout << (int)VSMsg.getCurrent() << " mA" << endl;
	}


	// -------- Transmitting a message --------
	//data to send:
	uint8_t newData[8] = {0xB8, 0x0B, 2, 0xA0, 0x41, 2, 0xC4, 0x09};
	Vehicle_Status_Message newMsg(newData);
	// TODO: add away to get access to data buffer in newMsg



}