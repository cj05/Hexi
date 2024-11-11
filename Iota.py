class Iota:
  iotatype = "placeholder"
  def __init__(self, value):
    self.setData(value)

  def getType():
    return self.type
    
  def setData(self, value):
    self.data = value

  def setValue(self, value):
    self.setData(value)

  def getData(self):
    return self.data

  def getValue(self):
    return self.getData()

  def getString(self):
    return self.data

  @classmethod
  def isSameType(cls, iota):
    return cls.iotatype == iota.iotatype

  #def fromDucky(self, value):
  #  self.data = value

  #def toDucky(self, value):
  #  self.data = value

  #def fromNbt(self, value):
  #  self.data = value

  #def toNbt(self, value):
  #  self.data = value

class GarbageIota(Iota):
  iotatype = "garbage"
  def __init__(self):
    self.setData(None)
  def setData(self, value):
    self.data = None


class StringIota(Iota):
  iotatype = "string"
  def setData(self, value):
    self.data = str(value)


class NumberIota(Iota):
  iotatype = "number"
  def setData(self, value):
    self.data = float(value)

  def getInt(self):
    return int(self.data)
  
