__author__ = 'michal'
import dpkt


class TcpReassembler():
    def __init__(self):
        self.stream = {}
        self.waiting = {}
        self.closing = {}


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

            self.stream[cs] = {}
            self.waiting[cs] = {}
            self.closing[cs] = {}

            self.stream[cs][p] = tcp.data

        elif ack_flag and not syn_flag and not fin_flag:  # only ack

            if len(tcp.data) > 0 and cs in self.stream:  # som data
                p = (tcp.seq, tcp.seq + len(tcp.data))

                if cs not in self.waiting:
                    self.waiting[cs] = {}

                self.waiting[cs][p] = tcp.data

            else:  # only ack without data
                pass

        elif fin_flag and not syn_flag:  # (fin), (fin, ack)
            p = (tcp.seq, tcp.seq + 1)

            self.closing[cs] = {}
            self.closing[cs][p] = tcp.data

        elif rst_flag and not syn_flag:  # (rst), (rst, ack)
            # if reset flag then remove all received data in both direction
            cs_r = (cs[1], cs[0])

            if cs in self.stream:
                self.stream.pop(cs)
                self.closing.pop(cs)
                self.waiting.pop(cs)

            if cs_r in self.stream:
                self.stream.pop(cs_r)
                self.closing.pop(cs_r)
                self.waiting.pop(cs_r)

        # try concat waiting packet to stream

        any_changes = True
        while any_changes:

            any_changes = False

            for c in self.waiting:

                c_key = None
                for (cs, cns) in self.waiting[c]:
                    if not c_key and cs in [ns for (s, ns) in self.stream[c]]:
                        c_key = (cs, cns)
                        any_changes |= True

                if c_key is not None:
                    data = self.waiting[c].pop(c_key)
                    self.stream[c][c_key] = data

        # sort packets in each stream and concat data
        # then remove all packet in each stream except for last one
        # for last one packet in stream set data as None

        for s in self.stream:
            if s not in result_data:
                result_data[s] = ''
            sorted_keys = sorted(self.stream[s].keys(), key=lambda tup: tup[0])
            for k in sorted_keys:
                if self.stream[s][k] is not None and len(self.stream[s][k]) > 0:
                    result_data[s] = result_data[s].join(self.stream[s][k])
                if k != sorted_keys[-1]:
                    self.stream[s].pop(k)
                else:
                    self.stream[s][k] = None

        # zamykanie
        # DONE: add closing stream (when finn then return None and delete stream from self.strem (how send end if result[streamtoclose] is not empty))

        any_changes = True
        while any_changes:

            any_changes = False

            for c in self.closing.keys():

                c_key = None
                for (cs, cns) in self.closing[c]:
                    if not c_key and c in self.stream and cs in [ns for (s, ns) in self.stream[c]]:
                        c_key = (cs, cns)
                        any_changes |= True

                if c_key is not None:
                    self.stream.pop(c)
                    self.closing.pop(c)
                    self.waiting.pop(c)
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
