import os, sys, time, subprocess, random


class COLOR:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
   
   def RGB(r, g, b):
       return f"\x1b[38;2;{int(r)};{int(g)};{int(b)}m"
   
   def XTerm_256(r, g, b):
    index = 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)

    if index < 16:
        return f"\033[{index}m"
    else:
        return f"\033[38;5;{index}m"
    


class Network:
    def __init__(self, host, count, timeout, delay, packet_size, resolution):
        self.host = host
        self.count = count
        self.timeout = timeout
        self.delay = delay
        self.packet_size = packet_size
        self.resolution = resolution
        self.command = ["ping", "-c 1", f"-t {self.timeout}", f"-s {self.packet_size}", self.host]
        self.responses = []
        self.packets_lost = 0
        
    
    def GetDistribution(self, resolution=16):
        results = []
        Pmax = max(self.responses)
        Pmin = min(self.responses)
        step = (Pmax - Pmin) / resolution
        
        for index in range(resolution):
            loweer_limit = Pmin + index * step
            upper_limit = loweer_limit + step
            
            n = 0
            for response in self.responses:
                if response >= loweer_limit and (response < upper_limit or index == resolution - 1):
                    n += 1
            results.append((n, ((loweer_limit + upper_limit) / 2)))
        
        return results
    
    
    def PrintDistribution(self):
        results = self.GetDistribution(self.resolution)
        reversed_results = results[::-1]
        
        max_str_len = len(str(max(results, key=lambda x: x[1])[1]).split('.')[0])
        
        for i in range(resolution):
                value_str = str(round(reversed_results[i][1], 3))
                
                value_str =  " " * (max_str_len - len(value_str.split(".")[0])) + value_str
                value_str =  value_str + "0" * (3 - len(value_str.split(".")[1]))
                
                color = COLOR.XTerm_256(int(255 * (1 - (i / (self.resolution-1)))), int(255 * i / (self.resolution-1)), 0)
                doubles = int(reversed_results[i][0] / 2)
                singles = reversed_results[i][0] % 2
                print(value_str + "|" + color + "#" * doubles + "*" * singles + COLOR.END)
        
        
    def Test(self):
        print(f"=== {COLOR.CYAN}{self.host}{COLOR.END} ping statistics ===")
        for i in range(self.count):
            try:
                result = subprocess.check_output(self.command).decode('utf-8')
                # print(result)
                self.responses.append(float(result.split("time=")[1].split(" ")[0]))
            except Exception as e:
                self.packets_lost += 1
                # print(e)
            self.PrintLiveResults()
            time.sleep(self.delay)
            
        self.PrintResults()
        print((len(self.host) + 24) * "=")
        self.PrintDistribution()
        print((len(self.host) + 24) * "=")
        
        
    def PrintLiveResults(self):
        if len(self.responses) >= 2:
            avg_ping = round(sum(self.responses)/len(self.responses), 2)
            diff = (self.responses[-1] - avg_ping) / (avg_ping / 2)
            if diff > 1:
                diff = 1
            if diff < -1:
                diff = -1
                
            if diff >= 0:
                arrow = "↗"
                ping_color = COLOR.XTerm_256(255, 255-diff*255, 255-diff*255)
            else:
                arrow = "↘"
                ping_color = COLOR.XTerm_256(255+diff*255, 255, 255+diff*255)
            
            print(f" [{round(100 * (len(self.responses) + self.packets_lost) / self.count, 2)}%] Avg: {COLOR.CYAN}{avg_ping}ms{COLOR.END} {ping_color}[{arrow} {self.responses[-1]}]{COLOR.END}         ", end="\r")
            
            
    
    
    def PrintResults(self):
        if len(self.responses) + self.packets_lost == 0:
            print("-")
            return False
        
        packet_loss = self.packets_lost / (len(self.responses) + self.packets_lost)
        pl_color = COLOR.XTerm_256(255, int((1 - packet_loss)*255), int((1 - packet_loss)*255))
        if len(self.responses) > 0:
            avg_ping = round(sum(self.responses)/len(self.responses), 2)
            red_val = (avg_ping - min(self.responses)) / (max(self.responses) - min(self.responses))
            ping_color = COLOR.XTerm_256(red_val * 255, 255 - red_val * 255, 0)
            
            r1 = f"Max: {COLOR.XTerm_256(255,0,0)}{max(self.responses)}ms{COLOR.END}" + " "*24
            r2 = f"Avg: {ping_color}{avg_ping}ms{COLOR.END}"
            r3 = f"Min: {COLOR.XTerm_256(0,255,0)}{min(self.responses)}ms{COLOR.END}"
            r4 = f"Packet loss: {pl_color}{round(packet_loss*100, 2)}%{COLOR.END}"
            
            msg = r1 + "\n" + r2 + "\n" + r3 + "\n" + r4
            print(msg)
        else:
            r1 = f"Max: --ms" + " "*20
            r2 = f"Avg: --ms"
            r3 = f"Min: --ms"
            r4 = f"Packet loss: {pl_color}{round(packet_loss*100, 2)}%{COLOR.END}"
            msg = r1 + "\n" + r2 + "\n" + r3 + "\n" + r4
            print(msg)


def print_help_note():
    print(f"Usage: python {sys.argv[0]} [host] [count] [timeout] [delay] [packet_size] [Distribution resolution]")
    print(f"Example: python {sys.argv[0]} 8.8.8.8 50 5 0.2 56 16")


if __name__ == '__main__':
    try:
        if len(sys.argv) == 2 and (sys.argv[1] == "--help" or sys.argv[1] == "-help"):
            print_help_note()
            exit(0)
        host = sys.argv[1] if len(sys.argv) > 1 else "8.8.8.8"
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
        delay = float(sys.argv[4]) if len(sys.argv) > 4 else 0.2
        packet_size = int(sys.argv[5]) if len(sys.argv) > 5 else 56
        resolution = int(sys.argv[6]) if len(sys.argv) > 6 else 16
    except Exception as e:
        print(f"{COLOR.RED}{e}{COLOR.END}")
        print_help_note()
        exit(0)
        
    network = Network(host, count, timeout, delay, packet_size, resolution)
    network.Test()
    # network.responses = [1,2,3,3,3,3,4,5,6,7,8,8,8,8,8,9,10,11,12]
    # network.PrintDistribution()