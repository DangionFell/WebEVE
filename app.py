from flask import Flask, render_template, request
import yaml
import math

def getName(id, typeIDs):
  try:
    return(str(typeIDs[id]["name"]["en"]))
  except KeyError:
    return("Name not found")

def getStack(id, blueprints):
  try:
    return blueprints[id]["activities"]["manufacturing"]["products"][0]["quantity"]
  except:
    try:
      return blueprints[id]["activities"]["reaction"]["products"][0]["quantity"]
    except:
      return ("Stack size not found")

def getID(name, typeIDs):
  for m in typeIDs:
    if getName(m, typeIDs) == name:
      return(int(m))
  return ("ID not found")

def getMaterials(id, blueprints):
  try:
    return blueprints[id]["activities"]["manufacturing"]["materials"]
  except:
    try:
      return blueprints[id]["activities"]["reaction"]["materials"]
    except:
      return ("Material not found")

def getBlueprint (id, typeIDs):
  try:
    s = getID(getName(id, typeIDs) + " Blueprint", typeIDs)
    s1 = getID(getName(id, typeIDs) + " Reaction Formula", typeIDs)
    if s == s1:
      return("Blueprint not found")
    else:
      if s == "ID not found":
        return s1
      else:
        return s
  except:
    return("Blueprint not found")


def SameIdSum(a):
  i = 0
  while i < len(a):
    j = 0
    while j < len(a):
      if a[i]["typeID"] == a[j]["typeID"] and i != j:
        a[i]["quantity"] += a[j]["quantity"]
        a.pop(j)
      j += 1
    i += 1
  return a


app = Flask(__name__)
app.config['SECRET_KEY'] = '1111111111'
WTF_CSRF_ENABLED = True

@app.route('/', methods=['POST','GET'])
def main():
    with open("typeIDs.yaml", "r", encoding="utf-8") as file:
        typeIDs = yaml.safe_load(file)
    with open("blueprints.yaml", "r", encoding="utf-8") as file:
        blueprints = yaml.safe_load(file)
    if request.method == 'POST':
        list1 = []
        item = getBlueprint(getID(request.form.get('blueprintName', default=None, type=None), typeIDs), typeIDs)
        count = int(request.form.get('count', default=None, type=None))

        if item != "Blueprint not found":
            item = getMaterials(item, blueprints)

            k = 0
            for i in item:
                list1.append({'quantity': 0, 'typeID': 0})
                list1[k]["quantity"] = i["quantity"] * count
                list1[k]["typeID"] = i["typeID"]
                k += 1

            k = 0
            while k != len(list1):
                if getBlueprint(list1[k]["typeID"], typeIDs) != "Blueprint not found":
                    item = getMaterials(getBlueprint(list1[k]["typeID"], typeIDs), blueprints)
                    leng = len(list1)
                    c = 0
                    for i in item:
                        list1.append({'quantity': 0, 'typeID': 0})
                        list1[c + leng]["quantity"] = math.ceil(
                            list1[k]["quantity"] / getStack(getBlueprint(list1[k]["typeID"], typeIDs), blueprints)) * i["quantity"]
                        list1[c + leng]["typeID"] = i["typeID"]
                        c += 1
                    list1.pop(k)
                    list1 = SameIdSum(list1)
                else:
                    k += 1

            list1 = SameIdSum(list1)
            list_out = []
            k = 0
            for i in list1:
                list_out.append({'name': str, 'quantity': 0})
                list_out[k]['name'] = getName(i['typeID'], typeIDs)
                list_out[k]['quantity'] = i['quantity']
                k += 1
            return render_template('index.html', blueprintList= list_out)
        else:
            print(item)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run()
