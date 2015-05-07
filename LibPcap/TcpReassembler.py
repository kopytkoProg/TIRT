__author__ = 'michal'
import dpkt
import time

current_milli_time = lambda: int(round(time.time() * 1000))
time_threshold = 1000 * 100


class TcpReassembler():
    def __init__(self):
        self.stream = {}
        self.waiting = {}
        self.closing = {}

        self.s = {}

    def add_packet(self, tcp):
        """
        :param tcp:
        :type tcp: dpkt.tcp.TCP
        :return:
        """

        result_closed = []
        result_data = {}

        fin_flag = (tcp.flags & dpkt.tcp.TH_FIN) != 0
        syn_flag = (tcp.flags & dpkt.tcp.TH_SYN) != 0
        rst_flag = (tcp.flags & dpkt.tcp.TH_RST) != 0
        psh_flag = (tcp.flags & dpkt.tcp.TH_PUSH) != 0
        ack_flag = (tcp.flags & dpkt.tcp.TH_ACK) != 0
        urg_flag = (tcp.flags & dpkt.tcp.TH_URG) != 0
        ece_flag = (tcp.flags & dpkt.tcp.TH_ECE) != 0
        cwr_flag = (tcp.flags & dpkt.tcp.TH_CWR) != 0

        cs = (tcp.sport, tcp.dport)

        if syn_flag and not fin_flag:  # (sync), (sync, ack)
            p = (tcp.seq, tcp.seq + 1)
            self.s[cs] = {'stream': {p: tcp.data}, 'waiting': {}, 'closing': {}, 'time': current_milli_time()}

        elif ack_flag and not syn_flag and not fin_flag and cs in self.s:  # only ack

            if len(tcp.data) > 0 and cs in self.s:  # som data
                p = (tcp.seq, tcp.seq + len(tcp.data))
                self.s[cs]['waiting'][p] = tcp.data

            else:  # only ack without data
                pass

            self.s[cs]['time'] = current_milli_time()

        elif fin_flag and not syn_flag and cs in self.s:  # (fin), (fin, ack)
            p = (tcp.seq, tcp.seq + 1)
            self.s[cs]['closing'][p] = tcp.data

            self.s[cs]['time'] = current_milli_time()

        elif rst_flag and not syn_flag and cs in self.s:  # (rst), (rst, ack)
            # if reset flag then remove all received data in both direction
            cs_r = (cs[1], cs[0])

            if cs in self.s:
                self.s.pop(cs)
                result_closed.append(cs)

            if cs_r in self.s:
                self.s.pop(cs_r)
                result_closed.append(cs)

        # ------------------------------
        # remove old inactive tcp stream
        # ------------------------------

        for k in self.s.keys():
            if current_milli_time() - self.s[k]['time'] > time_threshold:
                self.s.pop(k)

        # -----------------------------------
        # try concat waiting packet to stream
        # -----------------------------------

        any_changes = True
        while any_changes:

            any_changes = False

            for c in self.s:

                c_key = None
                for (cs, cns) in self.s[c]['waiting']:
                    if not c_key and cs in [ns for (s, ns) in self.s[c]['stream']]:
                        c_key = (cs, cns)
                        any_changes |= True

                if c_key is not None:
                    data = self.s[c]['waiting'].pop(c_key)
                    self.s[c]['stream'][c_key] = data

        # ---------------------------------------------------------
        # sort packets in each stream and concat data
        # then remove all packet in each stream except for last one
        # for last one packet in stream set data as None
        # ---------------------------------------------------------

        for s in self.s:
            if s not in result_data:
                result_data[s] = ''
            sorted_keys = sorted(self.s[s]['stream'].keys(), key=lambda tup: tup[0])
            for k in sorted_keys:
                if self.s[s]['stream'][k] is not None and len(self.s[s]['stream'][k]) > 0:
                    result_data[s] += self.s[s]['stream'][k]
                if k != sorted_keys[-1]:
                    self.s[s]['stream'].pop(k)
                else:
                    self.s[s]['stream'][k] = None

        # --------------------------------------------------------------------------------------
        # zamykanie
        # DONE: add closing stream (when finn then return None and delete stream from self.strem
        # (how send end if result[streamtoclose] is not empty))
        # --------------------------------------------------------------------------------------
        any_changes = True
        while any_changes:

            any_changes = False

            for c in self.s.keys():  # (s['closing'] for s in self.s):# self.closing.keys():

                c_key = None
                for (cs, cns) in self.s[c]['closing']:
                    if not c_key and cs in [ns for (s, ns) in self.s[c]['stream']]:
                        c_key = (cs, cns)
                        any_changes |= True

                if c_key is not None:
                    self.s.pop(c)
                    result_closed.append(c)

        # print self.stream
        # print self.waiting
        # print self.closing

        return {'data': result_data, 'closed': result_closed}


if __name__ == "__main__":
    p1 = dpkt.tcp.TCP()
    p1.sport = 1
    p1.dport = 2
    p1.seq = 0
    p1.flags = dpkt.tcp.TH_SYN

    p2 = dpkt.tcp.TCP()
    p2.sport = 2
    p2.dport = 1
    p2.seq = 0
    p2.flags = dpkt.tcp.TH_SYN | dpkt.tcp.TH_ACK

    p3 = dpkt.tcp.TCP()
    p3.sport = 1
    p3.dport = 2
    p3.seq = 1
    p3.flags = dpkt.tcp.TH_ACK

    p4 = dpkt.tcp.TCP()
    p4.sport = 1
    p4.dport = 2
    p4.seq = 1
    p4.flags = dpkt.tcp.TH_ACK
    p4.data = 'asdfg'

    p5 = dpkt.tcp.TCP()
    p5.sport = 2
    p5.dport = 1
    p5.seq = 1
    p5.flags = dpkt.tcp.TH_ACK

    p6 = dpkt.tcp.TCP()
    p6.sport = 1
    p6.dport = 2
    p6.seq = 6
    p6.flags = dpkt.tcp.TH_RST

    r = TcpReassembler()
    print r.add_packet(p1)
    print r.add_packet(p2)
    print r.add_packet(p3)
    print r.add_packet(p6)
    print r.add_packet(p4)
    print r.add_packet(p5)
