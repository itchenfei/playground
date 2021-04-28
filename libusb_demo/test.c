#include <stdio.h>
#include "libusb.h"
#pragma comment(lib,"libusb-1.0.lib")


int main(void) {
	libusb_device_handle* devHandle = NULL;
	libusb_device* devPtr = NULL;
	libusb_device** devList = NULL;
	struct libusb_device_descriptor  devDesc;

	unsigned char              strDesc[256];
	int                        retVal = 0;
	ssize_t                    numUsbDevs = 0;
	ssize_t                    idx = 0;

	retVal = libusb_init(NULL);
	printf("retVal=%d\n", retVal);

	numUsbDevs = libusb_get_device_list(NULL, &devList);
	printf("numUsbDevs=%d\n", numUsbDevs);

	while (idx < numUsbDevs)
	{
		printf("\n[%lu]\n", idx);

		devPtr = devList[idx];

		retVal = libusb_open(devPtr, &devHandle);

		idx++;
		if (retVal != LIBUSB_SUCCESS) {
			continue;
		}

		retVal = libusb_get_device_descriptor(devPtr, &devDesc);
		if (retVal != LIBUSB_SUCCESS)
			break;

		printf("   iManufacturer = %d\n", devDesc.iManufacturer);
		if (devDesc.iManufacturer > 0)
		{
			retVal = libusb_get_string_descriptor_ascii
			(devHandle, devDesc.iManufacturer, strDesc, 256);
			if (retVal < 0)
				break;

			printf("   string = %s\n", strDesc);
		}


		printf("success");

	}

}