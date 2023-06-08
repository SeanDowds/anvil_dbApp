import anvil.server

anvil.server.connect("server_7H4WUF46LHBZE5AZNNVOPM4S-VFUBAVKSCYH72RXM")

@anvil.server.callable
def say_hi(name):
  response = ("Hello from you Macbook M1 uplink, %s!" % name)
  print('You are in your own Terminal - ',response)
  return response

anvil.server.wait_forever()
