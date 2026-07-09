DSI(clear and IPsec)
=====
DSI is an internal application which generate clear and ipsec packets and validate the NAC IP .

The flow for NAC loopback is from Host-CPK(Columbia Park) -HLP(Highland Park) -CPM -RMN(Rimmon ) -Loopback Modules    and back . 
The packet generation is done by an external application called as CI_ETh which is based on DPDK(data plane development kit) .
Support
-------
  * Contact: Deepak Tiwari <deepak.tiwari@intel.com>
  * Original author: Deepak Tiwari <deepak.tiwari@intel.com>
  * Bug reports: https://hsdes.intel.com/appstore/article/#/mfg_platform_val.sighting

