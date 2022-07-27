# pylint: skip-file

import shlex
import subprocess

DNS_BACKBONE = "8.8.8.8"


def ParsePingOutput(line):
    time_ms = "".join(shlex.split(line)[6:7])[5:]
    if time_ms:
        return str(int(float(time_ms) + 0.5))
    else:
        return line


def RunMultiPing(ip_array):
    procs = []
    for ip in ip_array:
        cmd_str = "ping -n -c 1 -t 1 " + ip
        p = subprocess.Popen(
            cmd_str, shell=True, stdout=subprocess.PIPE, universal_newlines=True
        )
        procs.append(p)
    out = []
    for p in procs:
        p.stdout.readline()  # Throw away first readline
        line = p.stdout.readline().rstrip()
        if line:
            out.append(ParsePingOutput(line))
        else:
            out.append("NET_ERR")
        p.wait()
    return out


def GetTraceRoute(dest_ip):
    """Returns a list of routes to 8.8.8.8 in [(name, ip), ...] form."""
    trace_route = []
    cmd = "traceroute " + dest_ip
    try:
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True
        )
        for line in iter(p.stdout.readline, ""):
            if line.startswith("  "):
                continue
            line = line.rstrip().replace("* ", "")
            tokens = shlex.split(line)
            try:
                name = tokens[1]
                ip = tokens[2].replace("(", "").replace(")", "")
                print(f"found: {name} ({ip})")
                trace_route.append((name, ip))
            except IndexError:
                print(f"Error tokenizing {line}, skipping")
    finally:
        p.kill()
    return trace_route


def Main():
    def IsIpPingable(ip):
        p = subprocess.Popen(
            "ping -c 5 -t 1 " + ip,
            shell=True,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        for line in iter(p.stdout.readline, ""):
            if "time=" in line:
                p.wait()
                return True
        print(ip + " is invalid")
        return False

    trace_route = GetTraceRoute("8.8.8.8")
    # Filter out ip's that won't ping fast.
    trace_route = [e for e in trace_route if IsIpPingable(e[1])]

    def MakeDataRow():
        ips = [e[1] for e in trace_route]
        times = RunMultiPing(ips)
        out_str = ""
        for t in times:
            out_str += "{0: ^16s} | ".format(t)
        return out_str

    def MakeHeaderRow():
        def sizeStr(s, n):
            if len(s) < n:
                return s
            else:
                s = s[0 : n - 3] + "..."
                return s

        tmp = []
        out_str = ""
        for name, ip in trace_route:
            tmp.append(ip)
            out_str += "{0: ^16s} | ".format(sizeStr(name, 16))
        out_str += "\n"
        for name, ip in trace_route:
            tmp.append(ip)
            out_str += "{0: ^16s} | ".format(ip)
        return "\n" + out_str + "\n"

    while True:
        print(MakeHeaderRow())
        for i in range(0, 50):
            row = MakeDataRow()
            print(row)


if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        pass
