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


	cout << endl;

	// -------- Transmitting a message --------
	//data to send:
	// uint8_t newData[8] = {0xB8, 0x0B, 2, 0xA0, 0x41, 2, 0xC4, 0x09};
	Vehicle_Status_Message newMsg;
	newMsg.setVoltage(10000);
	newMsg.setRPM(2000);
	newMsg.setCurrent(1000);
	cout << (int)newMsg.getRPM() << " rpm" << endl;
	cout << (int)newMsg.getVoltage() << " mV" << endl;
	cout << (int)newMsg.getCurrent() << " mA" << endl;
	cout << (int)newMsg.messageID << " ID" << endl;
	cout << (int)newMsg.dlc << " bytes in the message." << endl;

	// to send a message, use the getMsgData() member to get a pointer to the data array
	// transmit(newMsg.id, newMsg.getMsgData(), newMsg.dlc);



}