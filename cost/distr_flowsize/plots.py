import matplotlib.pyplot as plt

def cdf_plot(nums, xscales, xtitle, ytitle, outfile):
        lenth = len(nums)
        cdf = []
        for i in xscales:
                tmp_count = sum([1 for k in nums if k <= i])
                percentg = float(tmp_count) / float(lenth)
                cdf.append(percentg)

        plt.figure(1)
        plt.subplot(111)
        plt.semilogx(xscales, cdf)
	plt.xlabel(xtitle)
	plt.ylabel(ytitle)
        plt.savefig(outfile)
        plt.close()

