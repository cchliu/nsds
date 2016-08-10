import matplotlib.pyplot as plt

def cdf_plot_semilogx(nums, xscales, xlabel, ylabel, title, outfile):
        lenth = len(nums)
        cdf = []
        for i in xscales:
                tmp_count = sum([1 for k in nums if k <= i])
                percentg = float(tmp_count) / float(lenth)
                cdf.append(percentg)

        plt.figure(1)
        plt.subplot(111)
        plt.semilogx(xscales, cdf)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
        plt.savefig(outfile)
        plt.close()

def cdf_plot_x(nums, xscales, xlabel, ylabel, title, outfile):
        lenth = len(nums)
        cdf = []
        for i in xscales:
                tmp_count = sum([1 for k in nums if k <= i])
                percentg = float(tmp_count) / float(lenth)
                cdf.append(percentg)

        plt.figure(1)
        plt.subplot(111)
        plt.plot(xscales, cdf)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
        plt.savefig(outfile)
        plt.close()

def xy_plot(x, y, xlabel, ylabel, outfile):
        plt.figure(1)
        plt.subplot(111)
        plt.plot(x,y)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
        plt.savefig(outfile)
	plt.close()

