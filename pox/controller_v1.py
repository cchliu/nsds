from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


UD_MISS_SEND_LEN = 0xffff      # 65535
UD_IDLE_TIMEOUT = 90
UD_HARD_TIMEOUT = 600

class Mycontroller(object):
        def __init__(self):
                self.connections = set()
                core.openflow.addListeners(self)

		self.count_packetIn = 0
                core.openflow.miss_send_len = 0xffff
                log.info("Requesting full packet payloads")

        def _handle_ConnectionUp(self, event):
                # Keep track of the connection to the switch so that we can 
                # send it messages
                connection = event.connection
                self.connections.add(connection)
                log.info("Switch %s has come up.", event.dpid)

                # ofp_set_config
                msg = of.ofp_set_config(miss_send_len = UD_MISS_SEND_LEN)
                #msg.miss_send_len = 65535
		connection.send(msg)
	
                # Request for ofp_desc_stats
                #msg = of.ofp_stats_request(body=of.ofp_desc_stats_request())
		#connection.send(msg)

        def _handle_SwitchDescReceived(self, event):
                # Handle reply from ofp_desc_request
                log.info('SwitchDescReceived from switch %s', event.dpid)
                # processed stats
                stats = event.stats

        def _handle_PacketIn(self, event):
		self.count_packetIn += 1
                # Handle packet in messages from switch
                log.info('PacketIn received from switch %s, port %s: %s', event.dpid, event.port, self.count_packetIn)
                packet = event.parsed # This is the parsed packet data.
		in_port = event.port
                connection = event.connection
                if not packet.parsed:
                        log.warning("Ignoring incomplete packet")
                        return

                #packet_in = event.ofp # The actual ofp_packet_in message.

                # Resend packet_in out
                msg = of.ofp_packet_out()
                msg.buffer_id = event.ofp.buffer_id
                msg_in_port = event.port
                msg.actions.append(of.ofp_action_output(port=in_port))
                connection.send(msg)

                # Define a match from an existing packet
                match = of.ofp_match.from_packet(packet)
                dl_type, proto, src_ip, src_port, dst_ip, dst_port = match.dl_type, match.nw_proto, match.nw_src, match.tp_src, match.nw_dst, match.tp_dst
                #idle_timeout = 15      # default value for NetFlow flow-cache timeout inactive
                #hard_timeout = 60
		
                # Install a new flow entry
                new_match = of.ofp_match()
		new_match.dl_type, new_match.nw_proto = dl_type, proto 
		new_match.nw_src, new_match.tp_src, new_match.nw_dst, new_match.tp_dst = src_ip, src_port, dst_ip, dst_port 
                log.info('Installing a new flow entry...')
		actions = []
		actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
                connection.send(of.ofp_flow_mod(command=of.OFPFC_ADD,
						actions = actions, 
						priority = 100, 
						match=new_match))
		print "return from installing a new flow entry..."	
		"""
                # Resend packet_in out
		msg = of.ofp_packet_out()
		msg.buffer_id = event.ofp.buffer_id
		msg_in_port = event.port
		msg.actions.append(of.ofp_action_output(port=in_port))
		connection.send(msg)
		"""

def launch():
        core.registerNew(Mycontroller)

