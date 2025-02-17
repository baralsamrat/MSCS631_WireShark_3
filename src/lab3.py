#!/usr/bin/env python3
import os
import subprocess
import pyshark
import time

def get_wifi_interface():
    """
    Automatically detects and returns the Wi-Fi interface number using tshark.
    Looks for an interface with 'Wi-Fi' or 'Wireless' in its description.
    """
    interfaces_output = subprocess.run(["tshark", "-D"], capture_output=True, text=True).stdout.splitlines()
    for interface in interfaces_output:
        if "Wi-Fi" in interface or "Wireless" in interface:
            # Example output line: "4. Wi-Fi (your adapter name)"
            return interface.split(" ", 1)[0].strip().replace(".", "")
    print("Error: No Wi-Fi interface found!")
    exit(1)

# Automatically detect the Wi-Fi interface ID
INTERFACE = get_wifi_interface()

def start_capture(output_file, duration=10):
    """
    Starts capturing UDP packets on the detected Wi-Fi interface.
    The capture filter is set to "udp" and runs for a specified duration.
    """
    print(f"📡 Starting UDP capture on interface {INTERFACE} for {duration} seconds...")
    # Note: The capture filter (-f "udp") is used because display filters (-Y) are not supported in capture mode.
    capture_command = f'tshark -i {INTERFACE} -a duration:{duration} -f "udp" -w {output_file}'
    proc = subprocess.Popen(capture_command, shell=True)
    return proc

def run_udp_server():
    """
    Launches the UDP server (server.py) as a subprocess.
    Make sure server.py is available and listens on the expected port (e.g., 9999).
    """
    print("📡 Starting UDP server...")
    server_proc = subprocess.Popen(["python", "server.py"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    return server_proc

def run_udp_client():
    """
    Runs the UDP client (client.py) as a subprocess.
    The client sends a UDP packet (e.g., "Hello, UDP server!") to the server.
    """
    print("📡 Running UDP client...")
    client_proc = subprocess.Popen(["python", "client.py"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    stdout, stderr = client_proc.communicate()
    print(stdout.decode())
    if stderr:
        print(stderr.decode())

def analyze_udp_packets(pcap_file, timeout=15):
    """
    Waits for the PCAP file to appear, then analyzes UDP packets using PyShark.
    Returns a list of captured UDP packets.
    """
    start_time = time.time()
    while not os.path.exists(pcap_file):
        if time.time() - start_time > timeout:
            print("❌ Error: PCAP file not found, exiting.")
            return []
        print("⏳ Waiting for PCAP file to appear...")
        time.sleep(2)
    
    print(f"🔍 Analyzing UDP packets in {pcap_file}...")
    capture = pyshark.FileCapture(pcap_file, display_filter="udp")
    packets = list(capture)
    capture.close()
    return packets

def answer_questions(udp_packets):
    """
    Analyzes the captured UDP packets and prints answers to the lab-3 questions.
    """
    print("\n=== UDP Analysis and Lab 3 Answers ===\n")
    
    if not udp_packets:
        print("No UDP packets captured.")
        return

    # ------------------------------
    # Question 1
    # ------------------------------
    print("Question 1:")
    first_packet = udp_packets[0]
    pkt_number = first_packet.number if hasattr(first_packet, "number") else "N/A"
    print(f"  a) The first UDP segment captured has packet number: {pkt_number}.")
    print("  b) The application-layer payload appears to be a raw text message (e.g., 'Hello, UDP server!').")
    print("  c) The UDP header contains 4 fields:")
    print("       - Source Port")
    print("       - Destination Port")
    print("       - Length")
    print("       - Checksum")
    
    # ------------------------------
    # Question 2
    # ------------------------------
    print("\nQuestion 2:")
    print("  Each field in the UDP header is 2 bytes long.")
    
    # ------------------------------
    # Question 3
    # ------------------------------
    print("\nQuestion 3:")
    try:
        udp_length = int(first_packet.udp.length)
        print(f"  The UDP Length field is {udp_length} bytes.")
        print("  This length represents the total size of the UDP datagram (header plus payload).")
    except Exception as e:
        print("  Unable to retrieve the UDP Length field from the packet.")
    
    # ------------------------------
    # Question 4
    # ------------------------------
    print("\nQuestion 4:")
    max_payload = 65535 - 8  # Total size minus the 8-byte header.
    print(f"  The maximum number of bytes in a UDP payload is {max_payload} bytes.")
    
    # ------------------------------
    # Question 5
    # ------------------------------
    print("\nQuestion 5:")
    print("  The largest possible source port number is 65,535.")
    
    # ------------------------------
    # Question 6
    # ------------------------------
    print("\nQuestion 6:")
    try:
        ip_proto = first_packet.ip.proto
        print(f"  The IP header's Protocol field is: {ip_proto} (UDP's protocol number is 17 in decimal).")
    except Exception as e:
        print("  Unable to retrieve IP protocol field. (Reminder: UDP's protocol number is 17.)")
    
    # ------------------------------
    # Question 7
    # ------------------------------
    print("\nQuestion 7:")
    if len(udp_packets) < 2:
        print("  Not enough UDP packets captured to analyze a request-response pair.")
    else:
        request_packet = udp_packets[0]
        reply_packet = udp_packets[1]
        req_num = request_packet.number if hasattr(request_packet, "number") else "N/A"
        rep_num = reply_packet.number if hasattr(reply_packet, "number") else "N/A"
        try:
            req_src = request_packet.udp.srcport
            req_dst = request_packet.udp.dstport
            rep_src = reply_packet.udp.srcport
            rep_dst = reply_packet.udp.dstport
        except Exception as e:
            req_src = req_dst = rep_src = rep_dst = "N/A"
        print(f"  Request Packet (packet number {req_num}):")
        print(f"      Source Port: {req_src}")
        print(f"      Destination Port: {req_dst}")
        print(f"  Reply Packet   (packet number {rep_num}):")
        print(f"      Source Port: {rep_src}")
        print(f"      Destination Port: {rep_dst}")
        print("  Relationship: The reply packet typically swaps the source and destination ports from the request.")
    
if __name__ == "__main__":
    # Create a directory for the capture if it doesn't exist.
    pcap_file = os.path.join("data", "udp_capture.pcap")
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Set the capture duration (in seconds) to cover the UDP traffic.
    capture_duration = 20
    capture_proc = start_capture(pcap_file, duration=capture_duration)
    
    # Start the UDP server.
    udp_server_proc = run_udp_server()
    time.sleep(2)  # Allow time for the server to initialize.
    
    # Run the UDP client to generate traffic.
    run_udp_client()
    
    # Wait for the capture to finish.
    capture_proc.wait()
    
    # Terminate the UDP server.
    print("Terminating UDP server...")
    udp_server_proc.terminate()
    udp_server_proc.wait()
    
    # Analyze the captured UDP packets.
    udp_packets = analyze_udp_packets(pcap_file)
    
    # Answer the lab-3 questions based on the captured packets.
    answer_questions(udp_packets)
