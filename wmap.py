#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Nop Phoomthaisong (aka @MaYaSeVeN)'
__version__ = 'Wmap version 1.0 ( http://mayaseven.com )'

# Requirement
# sudo pip install selenium
# sudo apt-get install phantomjs #phantomjs version 1.4 not work  #install lasted version
import optparse
import sys
import xml.dom.minidom

from lib import makess, reverseip

def main():
    print "\n" + __version__

    usage = "Usage: python " + sys.argv[
        0] + " -k [Bing API Key] [IP_1] [IP_2] [IP_N] [Domain_1] [Domain_2] [Domain_N]\nUsage: python " + \
            sys.argv[
                0] + " -k [Bing API Key] -l [list file of IP address]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-k", "--key", dest="key", help="Bing API key")
    parser.add_option("-l", "--list", dest="file", metavar="FILE", help="list file of IP address")
    parser.add_option("-x", "--xml", dest="filexml", metavar="XML", help="Parses nmap XML (nmap -oX)")
    parser.add_option("-d", "--disable", action="store_false",
                      help="set this option to disable to recheck is that the domain is in IP address",
                      default=True)

    (options, args) = parser.parse_args()

    if not options.key or (not options.file and not options.filexml and len(args) == 0):
        print parser.format_help()
        print """
you need to..
1.register or use microsoft account for get Bing API key -> https://datamarket.azure.com/
2.choose free plan 5,000 Transactions/month -> https://datamarket.azure.com/dataset/bing/searchweb
        """
        exit(1)
    key = options.key
    recheck = options.disable
    file = options.file
    filexml = options.filexml

    if filexml:
        try:
            dict_target_from_nmap = parse_nmap_xml(filexml)
        except IOError:
            print "[-] Error: File does not appear to exist."
            exit(1)
        ip_target_from_nmap = dict_target_from_nmap.keys()
        reverseIP = reverseip.Revereip(ip_target_from_nmap, key, recheck, None)
        reverseIP.run()
        targets_from_reverseIP = reverseIP.final_result
        concat_targets = {}
        for i in targets_from_reverseIP.keys():
            for j in dict_target_from_nmap.keys():
                if i == j:
                    c = targets_from_reverseIP[i] + dict_target_from_nmap[j]
                    concat_targets.update({i: c})
        makeSS = makess.Makess(concat_targets)
        makeSS.run()
    else:
        reverseIP = reverseip.Revereip(args, key, recheck, file)
        reverseIP.run()
        makeSS = makess.Makess(reverseIP.final_result)
        makeSS.run()


def parse_nmap_xml(file):
    input_files = open(file, 'r')
    doc = xml.dom.minidom.parse(input_files)
    dict_target_from_nmap = {}
    for host in doc.getElementsByTagName("host"):
        addresses = host.getElementsByTagName("address")
        for address in addresses:
            targets_from_nmap = []
            if address.getAttribute("addrtype") == "ipv4":
                ip = address.getAttribute("addr")
            else:
                continue
            for port in host.getElementsByTagName("port"):
                for state in port.getElementsByTagName("state"):
                    if state.getAttribute("state") == "open":
                        for services in port.getElementsByTagName("service"):
                            targets_temp = []
                            if "http" in services.getAttribute("name").lower() or "https" in services.getAttribute(
                                    "name").lower() or port.getAttribute("portid") == "80" or port.getAttribute(
                                    "portid") == "443":
                                if "http" in services.getAttribute("name").lower():
                                    if "ssl" in services.getAttribute(
                                            "tunnel").lower() or "ssl" in services.getAttribute(
                                            "product").lower():
                                        targets_temp.append("https://")
                                    else:
                                        targets_temp.append("http://")
                                elif port.getAttribute("portid") == "443":
                                    targets_temp.append("https://")
                                elif "https" in services.getAttribute("name").lower() or "ssl" in services.getAttribute(
                                        "name").lower():
                                    targets_temp.append("https://")
                                else:
                                    targets_temp.append("http://")
                                targets_temp.append(ip)
                                targets_temp.append(":" + port.getAttribute("portid"))
                                targets_from_nmap.append(targets_temp)
                                dict_target_from_nmap.update({ip: targets_from_nmap})
                    else:
                        continue

    return dict_target_from_nmap


if __name__ == "__main__":
    main()