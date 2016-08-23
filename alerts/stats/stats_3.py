import csv
from plots import xyy_plot_semilogx

def distr_sids(infile, postfix):
	result = []
	with open(infile, 'rb') as ff:
		reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for line in reader:
			sid, alerts_num, flows_num, priority, classification, msg = line[:6]
			sid, alerts_num, flows_num = int(sid), int(alerts_num), int(flows_num)
			result.append(flows_num)

	ranking = [i+1 for i in range(len(result))]
	total_flows = sum(result)
	y2 = [float(k)/float(total_flows)*100 for k in result]
	outfile = "distr_sids_{0}".format(postfix)
	ylabel2 = "Percentage (%) over all attacking flows"
	kwargs = {"xlabel":"rank", "ylabel":"Number of flows triggering the rule", "ylabel2":ylabel2, "title":"", "outfile":outfile}
	xyy_plot_semilogx(ranking, result, y2, **kwargs)

def main():
	infile = 'table_sid_frequency_0530_security_ET.csv'
	distr_sids(infile, '0530_securityET')

if __name__ == "__main__":
	main()
