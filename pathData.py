class pathData:
    CostPerMile = 20
    CostPerLandTakeoff = 5386
    NumofAirports = 6
    NetworkPopulation = 13696335
    Node_One = "airport_one"
    Node_Two = "airport_two"
    DISTANCE = 0
    CONNECTION = 0
    A1_POPULATION = 0
    A2_POPULATION = 0
    TOTALPOPSERVED = 0
    TOTALCOST = 0
    DISTANCE_VS_DIRECT = 0
    COST_VS_DIRECT = 0
    PATHSATISFACTION = 0
    WEIGHTED_SATISFACTION = 0


    def __init__(self, airport_one, airport_two, distance, connection, a1population, a2population):
        self.AIRPORT_ONE = airport_one
        self.AIRPORT_TWO = airport_two
        self.DISTANCE = distance
        self.CONNECTION = connection
        self.A1POPULATION = a1population
        self.A2POPULATION = a2population
        self.TOTALPOPSERVED = a1population + a2population
        self.TOTALCOST = distance*self.CostPerMile + (connection*self.CostPerLandTakeoff)+ self.CostPerLandTakeoff


    def printData(self):
        print(
            f"Route: {self.AIRPORT_ONE[0]} -> {self.AIRPORT_TWO[0]}\n"
            f"  Distance: {self.DISTANCE:,} mi\n"
            f"  Connections: {self.CONNECTION}\n"
            f"  Population Served: {self.TOTALPOPSERVED:,} "
            f"({self.A1POPULATION:,} + {self.A2POPULATION:,})\n"
            f"  Total Cost: ${self.TOTALCOST:,.2f}\n"
            f"  Distance vs Direct: {self.DISTANCE_VS_DIRECT}%\n"
            f"  Cost vs Direct: {self.COST_VS_DIRECT}%\n"
            f"  Path Satisfaction: {self.PATHSATISFACTION}%\n"
        )

    def getData(self,datatype):
        if datatype == "distance":
            return self.DISTANCE
        elif datatype == "connection":
            return self.CONNECTION
        elif datatype == "population":
            return self.TOTALPOPSERVED
        elif datatype == "cost":
            return self.TOTALCOST
        elif datatype == "distvsdirect":
            return self.DISTANCE_VS_DIRECT
        elif datatype == "costvsdirect":
            return self.COST_VS_DIRECT
        elif datatype == "pathsatisfaction":
            return self.PATHSATISFACTION
        elif datatype == "W_Sat":
            return self.WEIGHTED_SATISFACTION
        return None

    def compareDirectFlight(self, directDistance,directCost):
        self.DISTANCE_VS_DIRECT = round(((self.DISTANCE - directDistance) / directDistance) * 100, 2)
        self.COST_VS_DIRECT = round((((directCost/self.TOTALCOST))*100),2)

    def calculateSatisfaction(self):
        self.PATHSATISFACTION = self.COST_VS_DIRECT - (self.CONNECTION / (self.NumofAirports-2)) * 100
        if self.PATHSATISFACTION < 0:
            self.PATHSATISFACTION = 0
        self.WEIGHTED_SATISFACTION = self.PATHSATISFACTION * ((self.TOTALPOPSERVED / self.NetworkPopulation))
