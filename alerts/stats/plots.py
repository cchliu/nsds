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

def xy_plot_semilogx(x, y, xlabel, ylabel, outfile):
	plt.figure(1)
	plt.subplot(111)
	plt.semilogx(x, y)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.savefig(outfile)
	plt.close()

def xyy_plot(x, y, y2, xlabel, ylabel, ylabel2, title, outfile):
        fig, ax1= plt.subplots()
        ax1.plot(x, y, 'b')
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel, color='b')
        for t1 in ax1.get_yticklabels():
                t1.set_color('b')

        ax2 = ax1.twinx()
        ax2.plot(x, y2, 'r--')
        ax2.set_ylabel(ylabel2, color='r')
        for t2 in ax2.get_yticklabels():
                t2.set_color('r')
        plt.title(title)
        plt.savefig(outfile)
        plt.close()

def xyy_plot_semilogx(x, y, y2, xlabel, ylabel, ylabel2, title, outfile):
        fig, ax1= plt.subplots()
        ax1.semilogx(x, y, 'b')
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel, color='b')
        for t1 in ax1.get_yticklabels():
                t1.set_color('b')

        ax2 = ax1.twinx()
        ax2.semilogx(x, y2, 'r--')
        ax2.set_ylabel(ylabel2, color='r')
        for t2 in ax2.get_yticklabels():
                t2.set_color('r')
        plt.title(title)
        plt.savefig(outfile)
        plt.close()
