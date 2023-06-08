import anvil.server

anvil.server.connect("server_7H4WUF46LHBZE5AZNNVOPM4S-VFUBAVKSCYH72RXM")

@anvil.server.callable
def say_hi(name):
  response = ("Hello from Heroku uplink, %s!" % name)
  print('You are in the Heroku Log - ',response)
  return response

anvil.server.wait_forever()
