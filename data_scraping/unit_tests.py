import numpy as np

html_test1 = '''
<table width="96%" border="0" cellspacing="0" cellpadding="0">
<tbody><tr valign="BOTTOM">
<th colspan="2" align="LEFT"><font size="1"><b>Five fiscal years ended September 29, 2007<br> </b></font><font size="1">(In millions, except share and per share amounts)<br></font>
<br></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2007</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2006</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2005</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2004</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2003</b></font><hr noshade=""></th>
</tr>
<tr bgcolor="#CCEEFF" valign="BOTTOM">
<td colspan="2"><font size="2">Net sales</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">24,006</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">19,315</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">13,931</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">8,279</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">6,207</font></td>
</tr>
<tr bgcolor="White" valign="BOTTOM">
<td colspan="2"><font size="2">Net income</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">3,496</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">1,989</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">1,328</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">266</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">57</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="BOTTOM">
<td colspan="2"><font size="2">Earnings per common share:</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
</tr>
<tr bgcolor="White" valign="BOTTOM">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="35%"><font size="2">Basic</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">4.04</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">2.36</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">1.64</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">0.36</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">0.08</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="BOTTOM">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="35%"><font size="2">Diluted</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">3.93</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">2.27</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">1.55</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">0.34</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">0.08</font></td>
</tr>
<tr bgcolor="White" valign="BOTTOM">
<td colspan="2"><font size="2">Cash dividends declared per common share</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">—</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="BOTTOM">
<td colspan="2"><font size="2">Shares used in computing earnings per share (in thousands):</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%"><font size="2">&nbsp;</font></td>
</tr>
<tr bgcolor="White" valign="BOTTOM">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="35%"><font size="2">Basic</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">864,595</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">844,058</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">808,439</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">743,180</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">721,262</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="BOTTOM">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="35%"><font size="2">Diluted</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">889,292</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">877,526</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">856,878</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">774,776</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">723,352</font></td>
</tr>
<tr bgcolor="White" valign="BOTTOM">
<td colspan="2"><font size="2">Cash, cash equivalents, and short-term investments</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">15,386</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">10,110</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">8,261</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">5,464</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">4,566</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="BOTTOM">
<td colspan="2"><font size="2">Total assets</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">25,347</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">17,205</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">11,516</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">8,039</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">6,817</font></td>
</tr>
<tr bgcolor="White" valign="BOTTOM">
<td colspan="2"><font size="2">Long-term debt (including current maturities)</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">304</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="BOTTOM">
<td colspan="2"><font size="2">Total liabilities</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">10,815</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">7,221</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">4,088</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">2,976</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">2,594</font></td>
</tr>
<tr bgcolor="White" valign="BOTTOM">
<td colspan="2"><font size="2">Shareholders' equity</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">14,532</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">9,984</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">7,428</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">5,063</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">4,223</font></td>
</tr>
</tbody></table>
'''
html_test2 = '''
<table cellspacing="0" cellpadding="0" width="100%" border="0" align="center">

<tbody><tr>
<td width="73%"></td>
<td valign="bottom" width="5%"></td>
<td></td>
<td></td>
<td valign="bottom" width="5%"></td>
<td></td>
<td></td>
<td valign="bottom" width="5%"></td>
<td></td>
<td></td></tr>
<tr>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom" colspan="2" nowrap="" align="center" style="border-bottom:1px solid #000000"><font face="Times New Roman" size="1"><b>Fiscal<br>2006</b></font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom" colspan="2" nowrap="" align="center" style="border-bottom:1px solid #000000"> <p style="margin-top:0px;margin-bottom:0px" align="center"><font face="Times New Roman" size="1"><b>Fiscal</b></font></p> <p style="margin-top:0px;margin-bottom:1px" align="center"><font face="Times New Roman" size="1"><b>2005</b></font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom" colspan="2" nowrap="" align="center" style="border-bottom:1px solid #000000"><font face="Times New Roman" size="1"><b>Fiscal<br>2004</b></font></td></tr>
<tr>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom" colspan="8" align="center"><font face="Times New Roman" size="1"><b>(dollars in millions)</b></font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Revenues:</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Investment banking</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">4,318</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">3,477</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">3,008</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Principal transactions:</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td></tr>
<tr>
<td valign="top"> <p style="margin-left:5.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Trading</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">11,272</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">6,906</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">4,998</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:5.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Investments</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">1,477</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">656</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">364</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Commissions</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">2,606</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">2,160</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">1,998</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Asset management, distribution and administration fees</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">259</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">152</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">144</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Interest and dividends</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">41,979</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">25,455</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">16,395</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Other</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">404</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">301</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">190</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td></tr>
<tr>
<td valign="top"> <p style="margin-left:5.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Total revenues</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">62,315</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">39,107</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">27,097</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Interest expense</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">40,753</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">23,434</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">13,984</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td></tr>
<tr>
<td valign="top"> <p style="margin-left:5.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Net revenues</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">21,562</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">15,673</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">13,113</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Total non-interest expenses</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">13,402</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">10,919</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">8,832</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Income from continuing operations before losses from unconsolidated investees, income taxes, dividends on preferred securities subject to
mandatory redemption and cumulative effect of accounting change, net</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">8,160</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">4,754</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">4,281</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Losses from unconsolidated investees</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">225</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">311</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">328</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Provision for income taxes</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">2,308</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">909</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">932</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Dividends on preferred securities subject to mandatory redemption</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">—&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">—&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">45</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td>
<td valign="bottom" style="border-top:1px solid #000000">&nbsp;</td></tr>
<tr>
<td valign="top"> <p style="margin-left:5.00em; text-indent:-1.00em"><font face="Times New Roman" size="2">Income from continuing operations before cumulative effect of accounting change, net</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">5,627</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">3,534</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font face="Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font face="Times New Roman" size="2">2,976</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:3px double #000000">&nbsp;</td>
<td valign="bottom" style="border-top:3px double #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:3px double #000000">&nbsp;</td>
<td valign="bottom" style="border-top:3px double #000000">&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom" style="border-top:3px double #000000">&nbsp;</td>
<td valign="bottom" style="border-top:3px double #000000">&nbsp;</td></tr>
</tbody></table>
'''
html_test3 = '''
<p><font size="2"><b><i>Other Current Assets  </i></b></font></p>
<div align="CENTER"><table width="69%" border="0" cellspacing="0" cellpadding="0">
<tbody><tr valign="BOTTOM">
<th width="72%" align="LEFT"><font size="2">&nbsp;</font><br></th>
<th width="3%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2007</b></font><hr noshade=""></th>
<th width="3%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2006</b></font><hr noshade=""></th>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td width="72%"><font size="2">Vendor non-trade receivables</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">2,392</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">1,593</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td width="72%"><font size="2">NAND flash memory prepayments</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">417</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">208</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td width="72%"><font size="2">Other current assets</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">996</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="8%" align="RIGHT"><font size="2">469</font></td>
</tr>
<tr valign="TOP">
<td width="72%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td width="72%"><font size="2">Total other current assets</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">3,805</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="8%" align="RIGHT"><font size="2">2,270</font></td>
</tr>
<tr valign="TOP">
<td width="72%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade="" size="4"></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade="" size="4"></td>
</tr>
</tbody></table></div>
'''
html_test4 = '''
<p><font size="2"><b><i>Comprehensive Income  </i></b></font></p>
<p><font size="2">Comprehensive income consists of two components, net income and other comprehensive income. Other comprehensive income refers to revenue, expenses, gains, and losses that under
U.S. generally accepted accounting principles are recorded as an element of shareholders' equity but are excluded from net income. The Company's other comprehensive income consists of foreign currency
translation adjustments from those subsidiaries not using the U.S. dollar as their functional currency, unrealized gains and losses on marketable securities categorized as
available-for-sale, and net deferred gains and losses on certain derivative instruments accounted for as cash flow hedges. </font></p>
<p><font size="2">The
following table summarizes the components of accumulated other comprehensive income, net of taxes (in millions): </font></p>
<div align="CENTER"><table width="76%" border="0" cellspacing="0" cellpadding="0">
<tbody><tr valign="BOTTOM">
<th width="64%" align="LEFT"><font size="2">&nbsp;</font><br></th>
<th width="3%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2007</b></font><hr noshade=""></th>
<th width="3%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2006</b></font><hr noshade=""></th>
<th width="3%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2005</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td width="64%"><font size="2">Unrealized losses on available-for-sale securities</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="6%" align="RIGHT"><font size="2">(7</font></td>
<td width="3%"><font size="2">)</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="6%" align="RIGHT"><font size="2">—</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="6%" align="RIGHT"><font size="2">(4</font></td>
<td width="2%"><font size="2">)</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td width="64%"><font size="2">Unrealized gains on derivative instruments</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="6%" align="RIGHT"><font size="2">—</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="6%" align="RIGHT"><font size="2">3</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="6%" align="RIGHT"><font size="2">4</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td width="64%"><font size="2">Cumulative foreign currency translation</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="6%" align="RIGHT"><font size="2">70</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="6%" align="RIGHT"><font size="2">19</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="6%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
</tr>
<tr valign="TOP">
<td width="64%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td width="64%"><font size="2">Accumulated other comprehensive income</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="6%" align="RIGHT"><font size="2">63</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="6%" align="RIGHT"><font size="2">22</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">$</font></td>
<td width="6%" align="RIGHT"><font size="2">—</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
</tr>
<tr valign="TOP">
<td width="64%"><font size="2">&nbsp;</font></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade="" size="4"></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade="" size="4"></td>
<td width="3%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade="" size="4"></td>
<td width="2%"><font size="2">&nbsp;</font></td>
</tr>
</tbody></table></div>
'''
html_test5 = '''
<p align="CENTER"><font size="2"><a name="fe19701_consolidated_statements_of_ope__con03395"> </a>
<a name="toc_fe19701_1"> </a>
<br></font><font size="2"><b>CONSOLIDATED STATEMENTS OF OPERATIONS    <br>    <br>    (In millions, except share and per share amounts)    <br>    </b></font></p>
<table width="100%" border="0" cellspacing="0" cellpadding="0">
<tbody><tr valign="BOTTOM">
<th colspan="5" align="LEFT"><font size="1"><b>Three fiscal years ended September 29, 2007<br> </b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2007</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2006</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>2005</b></font><hr noshade=""></th>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td colspan="5"><font size="2">Net sales</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">24,006</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">19,315</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">13,931</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td colspan="5"><font size="2">Cost of sales (1)</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">15,852</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">13,717</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">9,889</font></td>
</tr>
<tr valign="TOP">
<td colspan="5"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td colspan="4"><font size="2">Gross margin</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">8,154</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">5,598</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">4,042</font></td>
</tr>
<tr valign="TOP">
<td colspan="5"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td colspan="5"><font size="2">Operating expenses:</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%"><font size="2">&nbsp;</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td colspan="4"><font size="2">Research and development (1)</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">782</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">712</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">535</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td colspan="4"><font size="2">Selling, general, and administrative (1)</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">2,963</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">2,433</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">1,864</font></td>
</tr>
<tr valign="TOP">
<td colspan="5"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="50%"><font size="2">Total operating expenses</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">3,745</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">3,145</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">2,399</font></td>
</tr>
<tr valign="TOP">
<td colspan="5"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td colspan="5"><font size="2">Operating income</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">4,409</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">2,453</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">1,643</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td colspan="5"><font size="2">Other income and expense</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">599</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">365</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">165</font></td>
</tr>
<tr valign="TOP">
<td colspan="5"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td colspan="5"><font size="2">Income before provision for income taxes</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">5,008</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">2,818</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">1,808</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td colspan="5"><font size="2">Provision for income taxes</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">1,512</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">829</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">480</font></td>
</tr>
<tr valign="TOP">
<td colspan="5"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade=""></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td colspan="5"><font size="2">Net income</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">3,496</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">1,989</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">1,328</font></td>
</tr>
<tr valign="TOP">
<td colspan="5"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade="" size="4"></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade="" size="4"></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td colspan="2" align="RIGHT"><hr noshade="" size="4"></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td colspan="5"><font size="2">Earnings per common share:</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%"><font size="2">&nbsp;</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="2%"><font size="0">&nbsp;</font></td>
<td colspan="3"><font size="2">Basic</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">4.04</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">2.36</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">1.64</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="2%"><font size="0">&nbsp;</font></td>
<td colspan="3"><font size="2">Diluted</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">3.93</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">2.27</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="9%" align="RIGHT"><font size="2">1.55</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td colspan="5"><font size="2"><br>
Shares used in computing earnings per share (in thousands):</font></td>
<td width="2%"><font size="2"><br>&nbsp;</font></td>
<td width="2%"><font size="2"><br>&nbsp;</font></td>
<td width="9%"><font size="2"><br>
&nbsp;</font></td>
<td width="2%"><font size="2"><br>&nbsp;</font></td>
<td width="2%"><font size="2"><br>&nbsp;</font></td>
<td width="9%"><font size="2"><br>
&nbsp;</font></td>
<td width="2%"><font size="2"><br>&nbsp;</font></td>
<td width="2%"><font size="2"><br>&nbsp;</font></td>
<td width="9%"><font size="2"><br>
&nbsp;</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="2%"><font size="0">&nbsp;</font></td>
<td colspan="3"><font size="2">Basic</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">864,595</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">844,058</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">808,439</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="2%"><font size="0">&nbsp;</font></td>
<td colspan="3"><font size="2">Diluted</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">889,292</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">877,526</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="9%" align="RIGHT"><font size="2">856,878</font></td>
</tr>
</tbody></table>
'''
html_test6 = '''
<p><font size="2"><b>Operating Expenses  </b></font></p>
<p><font size="2">Operating expenses for each of the last three fiscal years are as follows (in millions, except for percentages): </font></p>
<div align="CENTER"><table width="88%" border="0" cellspacing="0" cellpadding="0">
<tbody><tr valign="BOTTOM">
<th colspan="2" align="LEFT"><font size="2">&nbsp;</font><br></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>September 29,<br>
2007</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>September 30,<br>
2006</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
<th colspan="2" align="CENTER"><font size="1"><b>September 24,<br>
2005</b></font><hr noshade=""></th>
<th width="2%"><font size="1">&nbsp;</font></th>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td colspan="2"><font size="2">Research and development</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="14%" align="RIGHT"><font size="2">782</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="14%" align="RIGHT"><font size="2">712</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="14%" align="RIGHT"><font size="2">535</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="42%"><font size="2">Percentage of net sales</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="14%" align="RIGHT"><font size="2">3</font></td>
<td width="2%"><font size="2">%</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="14%" align="RIGHT"><font size="2">4</font></td>
<td width="2%"><font size="2">%</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="14%" align="RIGHT"><font size="2">4</font></td>
<td width="2%"><font size="2">%</font></td>
</tr>
<tr bgcolor="#CCEEFF" valign="TOP">
<td colspan="2"><font size="2">Selling, general, and administrative expenses</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="14%" align="RIGHT"><font size="2">2,963</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="14%" align="RIGHT"><font size="2">2,433</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">$</font></td>
<td width="14%" align="RIGHT"><font size="2">1,864</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
</tr>
<tr bgcolor="White" valign="TOP">
<td width="2%"><font size="0">&nbsp;</font></td>
<td width="42%"><font size="2">Percentage of net sales</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="14%" align="RIGHT"><font size="2">12</font></td>
<td width="2%"><font size="2">%</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="14%" align="RIGHT"><font size="2">13</font></td>
<td width="2%"><font size="2">%</font></td>
<td width="2%"><font size="2">&nbsp;</font></td>
<td width="14%" align="RIGHT"><font size="2">13</font></td>
<td width="2%"><font size="2">%</font></td>
</tr>
</tbody></table></div>
'''
html_test7 = '''
<p align="left"><font size="3"><b>Goldman Sachs Employees’ Profit Sharing Retirement Income Plan<br>
Statements of Net Assets Available for Benefits</b>
</font>

</p>
<p><font size="2"><i>As of November&nbsp;30<br>
In thousands</i>
</font>
</p>
<center>
<table cellspacing="0" border="0" cellpadding="0" width="100%">
<tbody><tr valign="bottom">
        <td width="5%">&nbsp;</td>
        <td width="5%">&nbsp;</td>
        <td width="50%">&nbsp;</td>
        <td width="5%">&nbsp;</td>
        <td width="7%">&nbsp;</td>
        <td width="1%">&nbsp;</td>
        <td width="7%">&nbsp;</td>
        <td width="5%">&nbsp;</td>
        <td width="7%">&nbsp;</td>
        <td width="1%">&nbsp;</td>
        <td width="7%">&nbsp;</td>
</tr>
<tr valign="bottom">
        <td><font size="1">&nbsp;</font></td>
        <td><font size="1">&nbsp;</font></td>
        <td><font size="1">&nbsp;</font></td>
        <td><font size="1">&nbsp;</font></td>
        <td nowrap="" align="center" colspan="3"><font size="1"><b>2001</b></font></td>
        <td><font size="1">&nbsp;</font></td>
        <td nowrap="" align="center" colspan="3"><font size="1"><b>2000</b></font></td>
</tr>
<tr valign="bottom">
        <td><font size="1">&nbsp;</font></td>
        <td><font size="1">&nbsp;</font></td>
        <td><font size="1">&nbsp;</font></td>
        <td><font size="1">&nbsp;</font></td>
        <td colspan="3"><hr size="1" noshade=""></td>
        <td><font size="1">&nbsp;</font></td>
        <td colspan="3"><hr size="1" noshade=""></td>
</tr>
<tr valign="bottom" bgcolor="#eeeeee">
        <td colspan="3"><div style="margin-left:10px; text-indent:-10px"><font size="2"><b>Assets</b></font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr><td>&nbsp;</td></tr>
<tr valign="bottom">
        <td colspan="3"><div style="margin-left:10px; text-indent:-10px"><font size="2">Interest in Goldman Sachs<br>
Profit Sharing Master Trust</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">$</font></td>
        <td align="right"><font size="2">2,269,939</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">$</font></td>
        <td align="right"><font size="2">2,246,896</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr>
        <td colspan="3"><div style="margin-left:10px; text-indent:-10px"><font size="2">&nbsp;</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="1" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="1" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr valign="bottom" bgcolor="#eeeeee">
        <td colspan="3"><div style="margin-left:10px; text-indent:-10px"><font size="2">Receivables:</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td>
</td></tr><tr valign="bottom">
        <td><font size="2">&nbsp;</font></td>
        <td colspan="2"><div style="margin-left:10px; text-indent:-10px"><font size="2">Employer contributions</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">45,749</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">37,839</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td>
</td></tr><tr valign="bottom" bgcolor="#eeeeee">
        <td><font size="2">&nbsp;</font></td>
        <td colspan="2"><div style="margin-left:10px; text-indent:-10px"><font size="2">Employee contributions</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">36,875</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">44,515</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr>
        <td colspan="3"><div style="margin-left:10px; text-indent:-10px"><font size="2">&nbsp;</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="1" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="1" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr valign="bottom">
        <td colspan="3"><div style="margin-left:10px; text-indent:-10px"><font size="2">&nbsp;</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">82,624</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">82,354</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr>
        <td colspan="3"><div style="margin-left:10px; text-indent:-10px"><font size="2">&nbsp;</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="1" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="1" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr valign="bottom" bgcolor="#eeeeee">
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><div style="margin-left:10px; text-indent:-10px"><font size="2"><b>Net assets available for benefits</b></font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">$</font></td>
        <td align="right"><font size="2">2,352,563</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">$</font></td>
        <td align="right"><font size="2">2,329,250</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr>
        <td colspan="3"><div style="margin-left:10px; text-indent:-10px"><font size="2">&nbsp;</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="4" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="4" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
</tbody></table>
</center>
'''
html_test8 = '''
<table cellspacing="0" border="0" cellpadding="0" width="92%">
<tbody><tr valign="bottom">
        <td width="70%">&nbsp;</td>
        <td width="5%">&nbsp;</td>
        <td width="4%">&nbsp;</td>
        <td width="1%">&nbsp;</td>
        <td width="5%">&nbsp;</td>
        <td width="5%">&nbsp;</td>
        <td width="4%">&nbsp;</td>
        <td width="1%">&nbsp;</td>
        <td width="5%">&nbsp;</td>
</tr>
<tr valign="bottom">
        <td><font size="1">&nbsp;</font></td>
        <td><font size="1">&nbsp;</font></td>
        <td nowrap="" align="center" colspan="7"><font size="1"><b>As of November 30,</b></font></td>
</tr>
<tr valign="bottom">
        <td nowrap=""><font size="1"><i>In thousands</i></font></td>
        <td><font size="1">&nbsp;</font></td>
        <td nowrap="" align="center" colspan="3"><font size="1"><b>2001</b></font></td>
        <td><font size="1">&nbsp;</font></td>
        <td nowrap="" align="center" colspan="3"><font size="1"><b>2000</b></font></td>
</tr>
<tr valign="top">
        <td nowrap="" align="center">&nbsp;</td>
        <td><font size="1">&nbsp;</font></td>
        <td colspan="3"><hr size="1" noshade=""></td>
        <td><font size="1">&nbsp;</font></td>
        <td colspan="3"><hr size="1" noshade=""></td>
</tr>
<tr valign="bottom" bgcolor="#eeeeee">
        <td><div style="margin-left:10px; text-indent:-10px"><font size="2">Net assets available for benefits per the
financial statements</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">$</font></td>
        <td align="right"><font size="2">2,352,563</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">$</font></td>
        <td align="right"><font size="2">2,329,250</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td>
</td></tr><tr valign="bottom">
        <td><div style="margin-left:10px; text-indent:-10px"><font size="2">Less: Amounts allocated to withdrawing participants</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">9,219</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">9,293</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr>
        <td><div style="margin-left:10px; text-indent:-10px"><font size="2">&nbsp;</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="1" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="1" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr valign="bottom" bgcolor="#eeeeee">
        <td><div style="margin-left:10px; text-indent:-10px"><font size="2">Net assets available for benefits per the Form&nbsp;5500</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">$</font></td>
        <td align="right"><font size="2">2,343,344</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td align="right"><font size="2">$</font></td>
        <td align="right"><font size="2">2,319,957</font></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
<tr>
        <td><div style="margin-left:10px; text-indent:-10px"><font size="2">&nbsp;</font></div></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="4" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><font size="2">&nbsp;</font></td>
        <td><hr size="4" noshade=""></td>
        <td><font size="2">&nbsp;</font></td>
</tr>
</tbody></table>
'''
html_test9 = '''
<table border="0" width="95%" align="center" cellpadding="0" cellspacing="0" style="font-size: 10pt; font-family: Arial, Helvetica; color: #000000; background: #FFFFFF">
<!-- Table Width Row BEGIN -->
<tbody><tr style="font-size: 1pt" valign="bottom">
    <td width="80%">&nbsp;</td>	<!-- colindex=01 type=maindata -->
    <td width="2%">&nbsp;</td>	<!-- colindex=02 type=gutter -->
    <td width="1%" align="right">&nbsp;</td>	<!-- colindex=02 type=lead -->
    <td width="1%" align="right">&nbsp;</td>	<!-- colindex=02 type=body -->
    <td width="1%" align="left">&nbsp;</td>	<!-- colindex=02 type=hang1 -->
    <td width="2%">&nbsp;</td>	<!-- colindex=03 type=gutter -->
    <td width="1%" align="right">&nbsp;</td>	<!-- colindex=03 type=lead -->
    <td width="1%" align="right">&nbsp;</td>	<!-- colindex=03 type=body -->
    <td width="1%" align="left">&nbsp;</td>	<!-- colindex=03 type=hang1 -->
    <td width="2%">&nbsp;</td>	<!-- colindex=04 type=gutter -->
    <td width="1%" align="right">&nbsp;</td>	<!-- colindex=04 type=lead -->
    <td width="1%" align="right">&nbsp;</td>	<!-- colindex=04 type=body -->
    <td width="1%" align="left">&nbsp;</td>	<!-- colindex=04 type=hang1 -->
    <td width="2%">&nbsp;</td>	<!-- colindex=05 type=gutter -->
    <td width="1%" align="right">&nbsp;</td>	<!-- colindex=05 type=lead -->
    <td width="1%" align="right">&nbsp;</td>	<!-- colindex=05 type=body -->
    <td width="1%" align="left">&nbsp;</td>	<!-- colindex=05 type=hang1 -->
</tr>
<!-- Table Width Row END -->
<!-- TableOutputHead -->
<tr style="font-size: 8pt" valign="bottom" align="center">
<td nowrap="" align="center" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td colspan="11" align="center" valign="bottom" style="border-bottom: 1px solid #000000">
    <b>Year Ended</b>
</td>
<td>
&nbsp;
</td>
<td colspan="3" nowrap="" align="center" valign="bottom" style="border-bottom: 1px solid #000000">
    <b>One Month Ended</b>
</td>
</tr>
<tr style="font-size: 8pt" valign="bottom" align="center">
<td nowrap="" align="center" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td colspan="3" nowrap="" align="center" valign="bottom">
    <b>December<br>
    </b>
</td>
<td>
&nbsp;
</td>
<td colspan="3" nowrap="" align="center" valign="bottom">
    <b>November<br>
    </b>
</td>
<td>
&nbsp;
</td>
<td colspan="3" nowrap="" align="center" valign="bottom">
    <b>November<br>
    </b>
</td>
<td>
&nbsp;
</td>
<td colspan="3" nowrap="" align="center" valign="bottom">
    <b>December<br>
    </b>
</td>
</tr>
<tr style="font-size: 8pt" valign="bottom" align="center">
<td nowrap="" align="center" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td colspan="3" nowrap="" align="center" valign="bottom" style="border-bottom: 1px solid #000000">
    <b>2009</b>
</td>
<td>
&nbsp;
</td>
<td colspan="3" nowrap="" align="center" valign="bottom" style="border-bottom: 1px solid #000000">
    <b>2008</b>
</td>
<td>
&nbsp;
</td>
<td colspan="3" nowrap="" align="center" valign="bottom" style="border-bottom: 1px solid #000000">
    <b>2007</b>
</td>
<td>
&nbsp;
</td>
<td colspan="3" nowrap="" align="center" valign="bottom" style="border-bottom: 1px solid #000000">
    <b>2008</b>
</td>
</tr>
<!-- TableOutputBody -->
<tr valign="bottom" style="background: #CCEEFF">
<td nowrap="" align="left" valign="bottom">
<div style="text-indent: -10pt; margin-left: 10pt">
    Net revenues
</div>
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    $
</td>
<td nowrap="" align="right" valign="bottom">
    45,173
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    $
</td>
<td nowrap="" align="right" valign="bottom">
    22,222
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    $
</td>
<td nowrap="" align="right" valign="bottom">
    45,987
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    $
</td>
<td nowrap="" align="right" valign="bottom">
    183
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
</tr>
<tr valign="bottom">
<td nowrap="" align="left" valign="bottom">
<div style="text-indent: -10pt; margin-left: 10pt">
    <font style="white-space: nowrap">Pre-tax</font>
    earnings/(loss)
</div>
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    19,829
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    2,336
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    17,604
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    (1,258
</td>
<td nowrap="" align="left" valign="bottom">
    )
</td>
</tr>
<tr valign="bottom" style="background: #CCEEFF">
<td nowrap="" align="left" valign="bottom">
<div style="text-indent: -10pt; margin-left: 10pt">
    Net earnings/(loss)
</div>
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    13,385
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    2,322
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    11,599
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    (780
</td>
<td nowrap="" align="left" valign="bottom">
    )
</td>
</tr>
<tr valign="bottom">
<td align="left" valign="bottom">
<div style="text-indent: -10pt; margin-left: 10pt">
    Net earnings/(loss) applicable to common shareholders
</div>
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    12,192
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    2,041
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    11,407
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    (1,028
</td>
<td nowrap="" align="left" valign="bottom">
    )
</td>
</tr>
<tr valign="bottom" style="background: #CCEEFF">
<td align="left" valign="bottom">
<div style="text-indent: -10pt; margin-left: 10pt">
    Diluted earnings/(loss) per common share
</div>
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    22.13
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    4.47
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    24.73
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    (2.15
</td>
<td nowrap="" align="left" valign="bottom">
    )
</td>
</tr>
<tr valign="bottom">
<td align="left" valign="bottom">
<div style="text-indent: -10pt; margin-left: 10pt">
    Return on average common shareholders’
    equity&nbsp;<sup style="font-size: 85%; vertical-align: top">(1)</sup>

</div>
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    22.5
</td>
<td nowrap="" align="left" valign="bottom">
    %
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    4.9
</td>
<td nowrap="" align="left" valign="bottom">
    %
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    32.7
</td>
<td nowrap="" align="left" valign="bottom">
    %
</td>
<td>
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
&nbsp;
</td>
<td nowrap="" align="right" valign="bottom">
    N.M.
</td>
<td nowrap="" align="left" valign="bottom">
&nbsp;
</td>
</tr>
</tbody></table>
'''
html_test10 = '''<table cellspacing="0" cellpadding="0" width="100%" border="0" style="BORDER-COLLAPSE:COLLAPSE" align="center">


<tbody><tr>
<td width="76%"></td>
<td valign="bottom" width="3%"></td>
<td></td>
<td></td>
<td></td>
<td valign="bottom" width="3%"></td>
<td></td>
<td></td>
<td></td></tr>
<tr>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom" colspan="6" align="center" style="border-bottom:1px solid #000000"><font style="font-family:Times New Roman" size="1"><b>December&nbsp;31,</b></font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td></tr>
<tr>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom" colspan="2" align="center" style="border-bottom:1px solid #000000"><font style="font-family:Times New Roman" size="1"><b>2011</b></font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom" colspan="2" align="center" style="border-bottom:1px solid #000000"><font style="font-family:Times New Roman" size="1"><b>2010</b></font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td></tr>


<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2"><b>Assets</b></font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Current assets:</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Cash and cash equivalents</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">9,883,777</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">907,879</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Short-term marketable securities</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">16,491</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,190,789</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Accounts receivable, net of allowances of $205,990 at December&nbsp;31, 2011 and $150,942 at December&nbsp;31,
2010</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,951,167</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,621,966</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Inventories</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,389,983</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,203,809</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Deferred tax assets</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">208,155</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">279,339</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Prepaid taxes</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">246,444</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">320,424</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Prepaid expenses</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">95,922</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">67,632</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Other current assets</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">126,846</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">116,244</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Total current assets</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">13,918,785</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">5,708,082</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Property, plant and equipment, net</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">774,406</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">701,235</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Noncurrent portion of prepaid royalties</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">174,584</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">203,790</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Noncurrent deferred tax assets</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">144,015</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">153,379</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Long-term marketable securities</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">63,704</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">3,219,403</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Intangible assets</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">2,066,966</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,425,592</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Other noncurrent assets</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">160,674</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">181,149</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Total assets</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">17,303,134</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">11,592,630</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2"><b>Liabilities and Stockholders’ Equity</b></font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Current liabilities:</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Accounts payable</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,206,052</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">803,025</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Accrued government rebates</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">516,045</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">325,018</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Accrued compensation and employee benefits</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">173,316</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">147,632</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Income taxes payable</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">40,583</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,862</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Other accrued liabilities</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">502,557</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">437,893</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Deferred revenues</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">74,665</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">103,175</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Current portion of convertible senior notes, net and other long-term obligations</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,572</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">646,345</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Total current liabilities</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">2,514,790</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">2,464,950</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Long-term deferred revenues</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">31,870</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">32,844</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Long-term debt, net</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">7,605,734</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">2,838,573</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Long-term income taxes payable</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">135,655</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">107,025</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Other long-term obligations</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">147,736</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">27,401</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Commitments and contingencies (Note 12)</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Stockholders’ equity:</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Preferred stock, par value $0.001 per share; 5,000 shares authorized; none outstanding</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">—&nbsp;&nbsp;</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">—&nbsp;&nbsp;</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Common stock, par value $0.001 per share; 2,800,000 shares authorized; 753,106 and 801,998 shares issued and outstanding at
December&nbsp;31, 2011 and 2010, respectively</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">753</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">802</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Additional paid-in capital</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">4,903,143</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">4,648,286</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Accumulated other comprehensive income</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">58,200</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">30,911</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Retained earnings</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,776,760</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">1,183,730</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Total Gilead stockholders’ equity</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">6,738,856</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">5,863,729</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Noncontrolling interest</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">128,493</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">258,108</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Total stockholders’ equity</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">6,867,349</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">6,121,837</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Total liabilities and stockholders’ equity</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">17,303,134</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">11,592,630</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
</tbody></table>'''
html_test11 = '''
<p style="margin-top:6px;margin-bottom:0px" align="center"><font style="font-family:Times New Roman" size="2"><b>Consolidated Statements of Cash Flows </b></font></p>
<p style="margin-top:0px;margin-bottom:0px" align="center"><font style="font-family:Times New Roman" size="2"><b>(in thousands) </b></font></p>
<table cellspacing="0" cellpadding="0" width="92%" border="0" style="BORDER-COLLAPSE:COLLAPSE" align="center">
<tbody><tr>
<td width="75%"></td>
<td valign="bottom" width="6%"></td>
<td></td>
<td></td>
<td></td>
<td valign="bottom" width="5%"></td>
<td></td>
<td></td>
<td></td></tr>
<tr>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom" colspan="6" align="center" style="border-bottom:1px solid #000000"><font style="font-family:Times New Roman" size="1"><b>December&nbsp;31,</b></font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td></tr>
<tr>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom" colspan="2" align="center" style="border-bottom:1px solid #000000"><font style="font-family:Times New Roman" size="1"><b>2011</b></font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom" colspan="2" align="center" style="border-bottom:1px solid #000000"><font style="font-family:Times New Roman" size="1"><b>2010</b></font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td></tr>


<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2"><b>Property, plant and equipment, net:</b></font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"></td>
<td valign="bottom"></td>
<td valign="bottom"></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Buildings and improvements (including leasehold improvements)</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">500,040</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">501,401</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Laboratory and manufacturing equipment</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">199,693</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">168,711</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Office and computer equipment</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">211,936</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">116,479</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Capitalized leased equipment</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">10,878</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">10,865</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:3.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Construction in progress</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">60,746</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">82,334</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:5.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Subtotal</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">983,293</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">879,790</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Less accumulated depreciation and amortization (including $10,546 and $10,451 relating to capitalized leased equipment for 2011
and 2010, respectively)</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">(358,263</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">)&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">(316,367</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">)&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:5.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Subtotal</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">625,030</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">563,423</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr>
<td valign="top"> <p style="margin-left:1.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Land</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">149,376</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">137,812</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;</td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:1px solid #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
<tr bgcolor="#cceeff">
<td valign="top"> <p style="margin-left:5.00em; text-indent:-1.00em"><font style="font-family:Times New Roman" size="2">Total</font></p></td>
<td valign="bottom"><font size="1">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">774,406</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td>
<td valign="bottom"><font size="1">&nbsp;</font></td>
<td valign="bottom"><font style="font-family:Times New Roman" size="2">$</font></td>
<td valign="bottom" align="right"><font style="font-family:Times New Roman" size="2">701,235</font></td>
<td nowrap="" valign="bottom"><font style="font-family:Times New Roman" size="2">&nbsp;&nbsp;</font></td></tr>
<tr style="font-size:1px">
<td valign="bottom"></td>
<td valign="bottom">&nbsp;&nbsp;</td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td>&nbsp;</td>
<td valign="bottom">&nbsp;</td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td valign="bottom"> <p style="border-top:3px double #000000">&nbsp;</p></td>
<td>&nbsp;</td></tr>
</tbody></table>
'''

html_test12 = '''
<p style="text-align:center;margin-bottom:0pt;margin-top:0pt;text-indent:0%;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;"><a name="BALANCE_SHEETS"></a><font style="font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;"><a name="BALANCE_SHEETS"></a>BALANCE</font><font style="font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;"> SHEETS</font></p>
<p style="margin-bottom:0pt;margin-top:0pt;text-align:justify;text-indent:0%;font-size:9pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p>
<div>
<table border="0" cellspacing="0" cellpadding="0" align="center" style="border-collapse:collapse; width:100%;">
<tbody><tr>
<td valign="bottom" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:7.5pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">(In millions)</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:2pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="2" valign="bottom" style="width:6%;">
<p style="line-height:2pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:2pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="2" valign="bottom" style="width:1%;">
<p style="line-height:2pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="8" valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="middle" style="width:82%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="4" valign="middle" style="width:6%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td colspan="3" valign="middle" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="middle" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:7.5pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">June 30,&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:2pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="2" valign="bottom" style="padding-left:0.7pt;padding-Right:0.7pt;padding-Top:0pt;padding-Bottom:0pt;width:6%;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:7.5pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">2019</p></td>
<td valign="bottom" style="width:1%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:2pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="2" valign="bottom" style="padding-left:0.7pt;padding-Right:0.7pt;padding-Top:0pt;padding-Bottom:0pt;width:1%;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:7.5pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">2018</p></td>
<td valign="bottom" style="width:1%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="middle" style="width:82%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="4" valign="middle" style="width:6%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td colspan="4" valign="middle" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">Assets</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Current assets:</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Cash and cash equivalents</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">11,356</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">11,946</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Short-term investments</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">122,463</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">121,822</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:justify;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:justify;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%; border-top:solid 0.75pt #000000;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-top:solid 0.75pt #000000;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-top:solid 0.75pt #000000;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-top:solid 0.75pt #000000;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="text-align:justify;line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:36pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total cash, cash equivalents, and short-term investments</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">133,819</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">133,768</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Accounts receivable, net of allowance for doubtful accounts of <font style="font-weight:bold;">$411</font> and $377</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">29,524</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">26,481</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Inventories</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">2,063</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">2,662</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Other</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">10,146</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">6,751</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:36pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total current assets</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">175,552</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">169,662</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Property and equipment, net of accumulated depreciation of <font style="font-weight:bold;">$35,330</font> and $29,223</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">36,477</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">29,460</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Operating lease right-of-use assets</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">7,379</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">6,686</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Equity investments</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">2,649</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">1,862</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Goodwill</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">42,026</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">35,683</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Intangible assets, net</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">7,750</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">8,053</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Other long-term assets</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">14,723</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">7,442</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:60pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total assets</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">286,556</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">258,848</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" style="width:82%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" style="width:82%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-top:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-top:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-top:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-top:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">Liabilities and stockholders’ equity</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Current liabilities:</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Accounts payable</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">9,382</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">8,617</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Current portion of long-term debt</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">5,516</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">3,998</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Accrued compensation</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">6,830</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">6,103</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Short-term income taxes</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">5,665</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">2,121</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Short-term unearned revenue</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">32,676</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">28,905</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Other</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">9,351</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">8,744</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:36pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total current liabilities</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">69,420</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">58,488</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Long-term debt</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">66,662</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">72,242</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Long-term income taxes</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">29,612</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">30,265</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Long-term unearned revenue</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">4,530</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">3,815</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Deferred income taxes</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">233</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">541</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Operating lease liabilities</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">6,188</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">5,568</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Other long-term liabilities</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">7,581</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">5,211</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:48pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total liabilities</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">184,226</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">176,130</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Commitments and contingencies</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:12pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Stockholders’ equity:</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Common stock and paid-in capital – shares authorized 24,000; outstanding <font style="font-weight:bold;">7,643</font> and&nbsp;7,677</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">78,520</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">71,223</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Retained earnings</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">24,150</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">13,682</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:24pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Accumulated other comprehensive loss</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">(340</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">)</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">(2,187</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">)&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:48pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total stockholders’ equity</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">102,330</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">82,718</p></td>
<td valign="bottom" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td colspan="4" valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-family:Times New Roman;font-size:11pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:6%;">
<p style="text-align:left;margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
<tr>
<td valign="top" bgcolor="#E5E5E5" style="width:82%;">
<p style="text-align:left;margin-bottom:0pt;margin-top:0pt;line-height:11pt;margin-left:60pt;;text-indent:-12pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total liabilities and stockholders’ equity</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">286,556</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;font-size:10pt;font-family:Arial;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:7.5pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:6%;">
<p style="text-align:right;line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">258,848</p></td>
<td valign="bottom" bgcolor="#E5E5E5" style="width:1%;white-space:nowrap;">
<p style="line-height:11pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:10pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" style="width:82%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%; border-bottom:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:6%; border-bottom:solid 1.5pt #000000;">
<p style="margin-top:0pt;line-height:4pt;border-top:none 0pt;padding-top:0pt;text-align:right;margin-bottom:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;font-family:Arial;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" style="width:1%;">
<p style="line-height:4pt;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-size:4pt;">&nbsp;</p></td>
</tr>
</tbody></table></div>
'''

html_test_13 = '''
<table border="1" cellpadding="0" cellspacing="0" style="border:none;border-collapse:collapse;width:100%;">
 <tbody><tr style="height:12.0pt;">
  <td colspan="10" valign="bottom" width="100%" style="background:white;border:none;height:12.0pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Times New Roman,serif" style="font-size:9.0pt;">Wells Fargo &amp; Company and Subsidiaries</font></p>
  </td>
 </tr>
<tr style="height:12.0pt;">
  <td colspan="10" valign="bottom" width="100%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:12.0pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Times New Roman,serif" style="font-size:9.0pt;">Consolidated
  Balance Sheet</font></b></p>
  </td>
 </tr>
<tr style="height:7.5pt;">
  <td colspan="10" valign="bottom" width="100%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="63%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="2" valign="bottom" width="11%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">December
  31,</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">(in millions, except shares)</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">2013&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">2012&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Assets</font></b></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Cash and due from banks</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">$&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;19,919&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;21,860&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Federal funds sold, securities purchased under resale agreements
  and other short-term investments</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;213,793&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;137,313&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Trading assets</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;62,813&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;57,482&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Investment securities:</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Available-for-sale, at fair value</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;252,007&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;235,199&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Held-to-maturity, at cost (fair value $12,247 and $0)</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;12,346&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;-&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Mortgages held for sale (includes $13,879 and $42,305 carried at
  fair value) (1)</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;16,763&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;47,149&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Loans held for sale (includes $1 and $6 carried at fair value)
  (1)</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;133&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;110&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:7.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="63%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Loans (includes $5,995 and $6,206 carried at fair value) (1)</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;825,799&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;799,574&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Allowance for loan losses</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;(14,502)&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;(17,060)&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Net loans</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;811,297&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;782,514&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Mortgage servicing rights:</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Measured at fair value</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;15,580&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;11,538&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Amortized</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,229&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,160&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Premises and equipment, net</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;9,156&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;9,428&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Goodwill</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;25,637&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;25,637&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Other assets (includes $1,386 and $0 carried at fair value) (1)</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;86,342&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;93,578&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="2" valign="bottom" width="66%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Total assets (2)</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">$&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,527,015&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,422,968&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Liabilities</font></b></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Noninterest-bearing deposits</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">$&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;288,117&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;288,207&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Interest-bearing deposits</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;791,060&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;714,628&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Total deposits</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,079,177&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,002,835&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Short-term borrowings</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;53,883&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;57,175&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Accrued expenses and other liabilities</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;69,949&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;76,668&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Long-term debt (includes $0 and $1 carried at fair value) (1)</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;152,998&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;127,379&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="3" valign="bottom" width="69%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Total liabilities (3)</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,356,007&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,264,057&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Equity</font></b></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Wells Fargo stockholders' equity:</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Preferred stock</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;16,267&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;12,883&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Common stock – $1-2/3 par value, authorized 9,000,000,000
  shares;</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="4" valign="bottom" width="72%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;issued 5,481,811,474 shares and 5,481,811,474 shares</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;9,136&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;9,136&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Additional paid-in capital</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;60,296&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;59,802&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Retained earnings</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;92,361&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;77,679&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Cumulative other comprehensive income</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,386&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;5,650&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Treasury stock – 224,648,769 shares and 215,497,298 shares</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;(8,104)&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;(6,610)&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="5" valign="bottom" width="75%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Unearned ESOP shares</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;(1,200)&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;(986)&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="4" valign="bottom" width="72%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Total Wells Fargo stockholders' equity</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;170,142&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;157,554&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:10.5pt;">
  <td colspan="6" valign="bottom" width="78%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Noncontrolling interests</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;866&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;border-bottom:solid black 1.0pt;height:10.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,357&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="3" valign="bottom" width="69%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Total equity</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;171,008&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:#CCEEFF;border:none;border-bottom:solid black 1.0pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;158,911&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:13.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td colspan="2" valign="bottom" width="66%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">Total liabilities and equity</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">$&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><b><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,527,015&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:7.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;border-bottom:solid black 1.5pt;height:13.5pt;padding:0in 0in 0in 0in;">
  <p align="right" style="margin:0in;margin-bottom:.0001pt;text-align:right;"><font color="black" face="Arial,sans-serif" style="font-size:7.0pt;">&nbsp;1,422,968&nbsp;</font></p>
  </td>
 </tr>
<tr style="height:7.5pt;">
  <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="63%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 <td valign="bottom" width="2%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p align="center" style="margin:0in;margin-bottom:.0001pt;text-align:center;"><b><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="9%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="3%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><b><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></b></p>
  </td>
 <td valign="bottom" width="8%" style="background:white;border:none;height:7.5pt;padding:0in 0in 0in 0in;">
  <p style="margin:0in;margin-bottom:.0001pt;"><font color="black" face="Verdana,sans-serif" style="font-size:8.0pt;">&nbsp;&nbsp;</font></p>
  </td>
 </tr>
</tbody></table>
'''
all_in_one_dict_gilead = all_in_one_dict ={'': {'CONSOLIDATED STATEMENT OF INCOME DATA:Income from operations': '3789841',
                                                'CONSOLIDATED STATEMENT OF INCOME DATA:Net income attributable to Gilead': '2803637',
                                                'CONSOLIDATED STATEMENT OF INCOME DATA:Net income per share attributable to Gilead common stockholders—basic': '3.62',
                                                'CONSOLIDATED STATEMENT OF INCOME DATA:Net income per share attributable to Gilead common stockholders—diluted': '3.55',
                                                'CONSOLIDATED STATEMENT OF INCOME DATA:Provision for income taxes': '861945',
                                                'CONSOLIDATED STATEMENT OF INCOME DATA:Shares used in per share calculation—basic': '774903',
                                                'CONSOLIDATED STATEMENT OF INCOME DATA:Shares used in per share calculation—diluted': '790118',
                                                'CONSOLIDATED STATEMENT OF INCOME DATA:Total costs and expenses (1)': '4595544',
                                                'CONSOLIDATED STATEMENT OF INCOME DATA:Total revenues': '8385385'},
                                           '2009': {'AmerisourceBergen Corp.': '12',
                                                    'Cardinal Health, Inc.': '17',
                                                    'Clinical studies and outside services': '570302',
                                                    'Impairment and restructuring charges': '26716',
                                                    'McKesson Corp.': '14',
                                                    'Other': '219670',
                                                    'Other:Total': '1229151',
                                                    'Personnel expenses': '412463'},
                                           '2010': {},
                                           'AVAILABLE-FOR-SALE SECURITIES': {},
                                           'Access in the Developing World': {},
                                           'AccumulatedAmortization': {},
                                           'AmBisome  is a proprietary liposomal formulation of amphotericin B, an antifungal agent to treat seriousinvasive fungal infections caused by various fungal species in adults. Our corporate partner, Astellas Pharma US, Inc., promotes and sells AmBisome in the United States and Canada, and we promote and sell AmBisome in Europe, Australia andNew Zealand.': {},
                                           'Antiviral Products': {},
                                           'Atripla': {},
                                           'Atripla .': {},
                                           'Balance at December 31, 2011': {},
                                           'Balance atEnd ofPeriod': {},
                                           'Business Highlights': {},
                                           'CERTAIN RELATIONSHIPS AND RELATED TRANSACTIONS, AND DIRECTOR INDEPENDENCE': {},
                                           'CHANGES IN AND DISAGREEMENTS WITH ACCOUNTANTS ON ACCOUNTING AND FINANCIAL DISCLOSURE': {},
                                           'COMPREHENSIVE INCOME': {'Less reclassification adjustments, net of tax impact of $(6,725), $(9,028) and $(32,532)for 2011, 2010 and 2009, respectively': '-55049',
                                                                    'Less reclassification adjustments, net of tax impact of $(6,725), $(9,028) and $(32,532)for 2011, 2010 and 2009, respectively:Other comprehensive income (loss)': '32553',
                                                                    'Net unrealized gain (loss) related to available-for-sale securities, net of tax impact of $(3,305), $(6,624) and $(11,724) for 2011, 2010 and 2009, respectively': '-24067',
                                                                    'Net unrealized gain (loss) related to cash flow hedges, net of tax impact of $(93), $(9,149) and $10,682 for 2011, 2010 and 2009, respectively': '1571'},
                                           'CONSOLIDATED BALANCE SHEET DATA:': {},
                                           'CONTENTS': {},
                                           'Calistoga Pharmaceuticals, Inc.': {},
                                           'Cardiovascular': {},
                                           'Cayston .': {},
                                           'Clinical Trials': {},
                                           'Commercial Collaborations': {},
                                           'Comparison of Cumulative Total Return on Investment for the Past Five Years': {},
                                           'Competition': {},
                                           'Complera/Eviplera is an oral formulation dosed once a day for the treatment of HIV-1 infection in treatment-naïve adults. The product,marketed in the United States as Complera and in Europe as Eviplera, is the second complete single-tablet regimen for the treatment of HIV and is a fixed-dose combination of our antiretroviral medications, Viread and Emtriva, and TibotecPharmaceuticals’ non-nucleoside reverse transcriptase inhibitor, Edurant .': {},
                                           'Consolidated Balance Sheets': {'Assets:Current assets:Accounts receivable, net of allowances of $205,990 at December\xa031, 2011 and $150,942 at December\xa031, 2010': '1951167',
                                                                           'Assets:Current assets:Cash and cash equivalents': '9883777',
                                                                           'Assets:Current assets:Deferred tax assets': '208155',
                                                                           'Assets:Current assets:Inventories': '1389983',
                                                                           'Assets:Current assets:Other current assets': '126846',
                                                                           'Assets:Current assets:Prepaid expenses': '95922',
                                                                           'Assets:Current assets:Prepaid taxes': '246444',
                                                                           'Assets:Current assets:Short-term marketable securities': '16491',
                                                                           'Assets:Intangible assets': '2066966',
                                                                           'Assets:Long-term marketable securities': '63704',
                                                                           'Assets:Noncurrent deferred tax assets': '144015',
                                                                           'Assets:Noncurrent portion of prepaid royalties': '174584',
                                                                           'Assets:Other noncurrent assets': '160674',
                                                                           'Assets:Property, plant and equipment, net': '774406',
                                                                           'Assets:Total assets': '17303134',
                                                                           'Assets:Total current assets': '13918785',
                                                                           'Liabilities and Stockholders’ Equity:Current liabilities:Accounts payable': '1206052',
                                                                           'Liabilities and Stockholders’ Equity:Current liabilities:Accrued compensation and employee benefits': '173316',
                                                                           'Liabilities and Stockholders’ Equity:Current liabilities:Accrued government rebates': '516045',
                                                                           'Liabilities and Stockholders’ Equity:Current liabilities:Current portion of convertible senior notes, net and other long-term obligations': '1572',
                                                                           'Liabilities and Stockholders’ Equity:Current liabilities:Deferred revenues': '74665',
                                                                           'Liabilities and Stockholders’ Equity:Current liabilities:Income taxes payable': '40583',
                                                                           'Liabilities and Stockholders’ Equity:Current liabilities:Other accrued liabilities': '502557',
                                                                           'Liabilities and Stockholders’ Equity:Long-term debt, net': '7605734',
                                                                           'Liabilities and Stockholders’ Equity:Long-term deferred revenues': '31870',
                                                                           'Liabilities and Stockholders’ Equity:Long-term income taxes payable': '135655',
                                                                           'Liabilities and Stockholders’ Equity:Noncontrolling interest': '128493',
                                                                           'Liabilities and Stockholders’ Equity:Other long-term obligations': '147736',
                                                                           'Liabilities and Stockholders’ Equity:Stockholders’ equity:Accumulated other comprehensive income': '58200',
                                                                           'Liabilities and Stockholders’ Equity:Stockholders’ equity:Additional paid-in capital': '4903143',
                                                                           'Liabilities and Stockholders’ Equity:Stockholders’ equity:Common stock, par value $0.001 per share; 2,800,000 shares authorized; 753,106 and 801,998 shares issued and outstanding at December\xa031, 2011 and 2010, respectively': '753',
                                                                           'Liabilities and Stockholders’ Equity:Stockholders’ equity:Preferred stock, par value $0.001 per share; 5,000 shares authorized; none outstanding': '—',
                                                                           'Liabilities and Stockholders’ Equity:Stockholders’ equity:Retained earnings': '1776760',
                                                                           'Liabilities and Stockholders’ Equity:Total Gilead stockholders’ equity': '6738856',
                                                                           'Liabilities and Stockholders’ Equity:Total current liabilities': '2514790',
                                                                           'Liabilities and Stockholders’ Equity:Total liabilities and stockholders’ equity': '17303134',
                                                                           'Liabilities and Stockholders’ Equity:Total stockholders’ equity': '6867349'},
                                           'Consolidated Statements of Cash Flows': {'Financing activities:Cash and cash equivalents at beginning of period': '907879',
                                                                                     'Financing activities:Cash and cash equivalents at end of period': '9883777',
                                                                                     'Financing activities:Contributions from (distributions to) noncontrolling interest': '-115037',
                                                                                     'Financing activities:Effect of exchange rate changes on cash': '-16526',
                                                                                     'Financing activities:Excess tax benefits from stock-based compensation': '40848',
                                                                                     'Financing activities:Extinguishment of long-term debt': '-649987',
                                                                                     'Financing activities:Net cash provided by (used in) financing activities': '1763569',
                                                                                     'Financing activities:Net change in cash and cash equivalents': '8975898',
                                                                                     'Financing activities:Proceeds from credit facility': '—',
                                                                                     'Financing activities:Proceeds from issuances of common stock': '211737',
                                                                                     'Financing activities:Proceeds from issuances of convertible notes, net of issuance costs': '—',
                                                                                     'Financing activities:Proceeds from issuances of senior notes, net of issuance costs': '4660702',
                                                                                     'Financing activities:Proceeds from sale of warrants': '—',
                                                                                     'Financing activities:Purchases of convertible note hedges': '—',
                                                                                     'Financing activities:Repayments of credit facility': '—',
                                                                                     'Financing activities:Repayments of long-term obligations': '-1562',
                                                                                     'Financing activities:Repurchases of common stock': '-2383132',
                                                                                     'Investing activities:Acquisitions, net of cash acquired': '-588608',
                                                                                     'Investing activities:Capital expenditures and other': '-131904',
                                                                                     'Investing activities:Net cash provided by (used in) investing activities': '3589845',
                                                                                     'Investing activities:Proceeds from maturities of marketable securities': '788395',
                                                                                     'Investing activities:Proceeds from sales of marketable securities': '8649752',
                                                                                     'Investing activities:Purchases of marketable securities': '-5127790',
                                                                                     'Operating activities:Net cash provided by operating activities': '3639010',
                                                                                     'Operating activities:Net income': '2789059',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Amortization expense': '230045',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Changes in operating assets and liabilities:Accounts payable': '428944',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Changes in operating assets and liabilities:Accounts receivable, net': '-375736',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Changes in operating assets and liabilities:Accrued liabilities': '300593',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Changes in operating assets and liabilities:Deferred revenues': '-29484',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Changes in operating assets and liabilities:Income taxes payable': '110771',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Changes in operating assets and liabilities:Inventories': '-200793',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Changes in operating assets and liabilities:Prepaid expenses and other assets': '-13959',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Deferred income taxes': '64061',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Depreciation expense': '72187',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Excess tax benefits from stock-based compensation': '-40848',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:In-process research and development impairment': '26630',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Other non-cash transactions': '47931',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Stock-based compensation expenses': '192378',
                                                                                     'Operating activities:Net income:Adjustments to reconcile net income to net cash provided by operating activities:Tax benefits from employee stock plans': '37231',
                                                                                     'Supplemental disclosure of cash flow information:Income taxes paid': '621025',
                                                                                     'Supplemental disclosure of cash flow information:Interest paid': '62180'},
                                           'Consolidated Statements of Income': {'Costs and expenses:Cost of goods sold': '2124410',
                                                                                 'Costs and expenses:Research and development': '1229151',
                                                                                 'Costs and expenses:Selling, general and administrative': '1241983',
                                                                                 'Income before provision for income taxes': '3651004',
                                                                                 'Income from operations': '3789841',
                                                                                 'Interest and other income, net': '66581',
                                                                                 'Interest expense': '-205418',
                                                                                 'Net income': '2789059',
                                                                                 'Net income attributable to Gilead': '2803637',
                                                                                 'Net income per share attributable to Gilead common stockholders—basic': '3.62',
                                                                                 'Net income per share attributable to Gilead common stockholders—diluted': '3.55',
                                                                                 'Net loss attributable to noncontrolling interest': '14578',
                                                                                 'Provision for income taxes': '861945',
                                                                                 'Revenues:Contract and other revenues': '14199',
                                                                                 'Revenues:Product sales': '8102359',
                                                                                 'Revenues:Royalty revenues': '268827',
                                                                                 'Shares used in per share calculation—basic': '774903',
                                                                                 'Shares used in per share calculation—diluted': '790118',
                                                                                 'Total costs and expenses': '4595544',
                                                                                 'Total revenues': '8385385'},
                                           'Consolidated Statements of Stockholders’ Equity': {},
                                           'Contractual Obligations': {},
                                           'Cost of Goods Sold and Product Gross Margin': {'Cost of goods sold': '2124410',
                                                                                           'Product gross margin': '74',
                                                                                           'Total product sales': '8102359'},
                                           'DIRECTORS, EXECUTIVE OFFICERS AND CORPORATE GOVERNANCE': {},
                                           'DOCUMENTS INCORPORATED BYREFERENCE': {},
                                           'Description of Document': {},
                                           'EXECUTIVE COMPENSATION': {},
                                           'EXHIBITS AND FINANCIAL STATEMENT SCHEDULES': {},
                                           'Expiration': {},
                                           'FAIR VALUE MEASUREMENTS': {},
                                           'FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA': {},
                                           'FORM 10-K': {},
                                           'Fair Value': {'Gross realized gains on sales': '42849',
                                                          'Gross realized losses on sales': '-12526'},
                                           'Financing Arrangements': {'April 2021 senior unsecured notes': '992066',
                                                                      'December 2014 senior unsecured notes': '749078',
                                                                      'December 2016 senior unsecured notes': '698864',
                                                                      'December 2021 senior unsecured notes': '1247138',
                                                                      'December 2041 senior unsecured notes': '997734',
                                                                      'December 2041 senior unsecured notes:Total debt, net': '7605734',
                                                                      'Less current portion (May 2011 convertible senior notes)': '—',
                                                                      'Less current portion (May 2011 convertible senior notes):Total long-term debt, net': '7605734',
                                                                      'May 2011 convertible senior notes': '—',
                                                                      'May 2013 convertible senior notes': '607036',
                                                                      'May 2014 convertible senior notes': '1181525',
                                                                      'May 2016 convertible senior notes': '1132293'},
                                           'Finite-Lived Intangible Assets': {'Gross\xa0CarryingAmount': 'AccumulatedAmortization',
                                                                              'Intangible asset - Lexiscan': '262800',
                                                                              'Intangible asset - Ranexa': '688400',
                                                                              'Other': '24995',
                                                                              'Other:Total': '976195'},
                                           'Foreign Currency Exchange Forward Contracts': {'Currency': 'NotionalAmount',
                                                                                           'Currency:Australian Dollar': '129025',
                                                                                           'Currency:British Pound': '305314',
                                                                                           'Currency:Canadian Dollar': '179785',
                                                                                           'Currency:Danish Krone': '1520',
                                                                                           'Currency:Euro': '3205266',
                                                                                           'Currency:New Zealand Dollar': '9304',
                                                                                           'Currency:Norwegian Krone': '17898',
                                                                                           'Currency:Polish Zloty': '25532',
                                                                                           'Currency:Polish Zloty:Total': '4026082',
                                                                                           'Currency:Swedish Krone': '31738',
                                                                                           'Currency:Swiss Franc': '110161',
                                                                                           'Currency:Turkish Lira': '10539'},
                                           'GILEADSCIENCES, INC.': {},
                                           'GSK. In 2006, we sublicensed to GSK exclusive rights to market ambrisentan  under the nameVolibris for PAH in territories outside of the United States. Under the license agreement, we received an up-front payment of $20.0 million and, subject to the achievement of specific milestones, we are eligible to receive total additional milestonepayments of $80.0 million. Through December 31, 2011, we have received $55.0 million of such potential milestone payments. In addition, we will receive royalties based on net sales of Volibris in the GSK territories. GSK has an option tonegotiate from us an exclusive sublicense for additional therapeutic uses for Volibris in the GSK territories during the term of the license agreement. Under the agreement, we will continue to conduct and bear the expense of all clinical developmentactivities that we believe are required to obtain and maintain regulatory approvals for Letairis and Volibris in the United States, Canada and the European Economic Area, and each party may conduct additional development activities in itsterritories at its own expense. The parties may agree to jointly develop ambrisentan for new indications in the licensed field, and each party will pay its share of external costs associated with such joint development. The agreement and GSK’sobligation to pay royalties to us will terminate on a country-by-country basis on the earlier of the date on which generic equivalents sold in a country achieve a certain percentage of total prescriptions for the product plus its generic equivalentsor the fifteenth anniversary of commercial launch in such country. GSK may terminate the agreement for any reason. Upon such termination, all rights to the product would revert to us. Either party may terminate the agreement in response to amaterial breach by the other party.': {},
                                           'Goodwill': {},
                                           'Government Rebates': {},
                                           'HIV/AIDS': {},
                                           'INCOME TAXES': {'Federal:772,803': '822968',
                                                            'Federal:Current': '704412',
                                                            'Federal:Deferred': '68391',
                                                            'Foreign:43,961': '43548',
                                                            'Foreign:Current': '39921',
                                                            'Foreign:Deferred': '4040',
                                                            'Provision for income taxes': '861945',
                                                            'State:45,181': '157283',
                                                            'State:Current': '62631',
                                                            'State:Deferred': '-17450'},
                                           'INTANGIBLE ASSETS': {'Finite-lived intangible assets': '796664',
                                                                 'Goodwill': '1004102',
                                                                 'Indefinite-lived intangible assets': '266200',
                                                                 'Indefinite-lived intangible assets:Total': '2066966'},
                                           'INVENTORIES': {'Finished goods': '225863',
                                                           'Finished goods:Total': '1389983',
                                                           'Raw materials': '697621',
                                                           'Work in process': '466499'},
                                           'If we fail to attract and retain highly qualified personnel, we may be unable to successfully develop new product candidates, conduct our clinical trials and commercialize our product candidates.': {},
                                           'Intangible Assets': {},
                                           'Interest Rate Risk': {'Assets:Available-for-sale debt securities': '1574140',
                                                                  'Assets:Average interest rate': '1.2',
                                                                  'Liabilities:Average interest rate': '0.0',
                                                                  'Liabilities:Long-term debt\xa0(1)': '—'},
                                           'International Partnership for Microbicides  and CONRAD. In 2006, we entered into an agreement under which we granted rights to IPM andCONRAD, a cooperating agency of the U.S. Agency for International Development committed to improving reproductive health by expanding the contraceptive choices of women and men, to develop, manufacture, and, if proven efficacious, arrange for thedistribution in resource limited countries of certain formulations of tenofovir for use as a topical microbicide to prevent HIV infection.': {},
                                           'Issuer Purchases of Equity Securities': {},
                                           'Lease Arrangements': {},
                                           'Letairis , for PAH interritories outside of the United States.': {},
                                           'Liabilities': {},
                                           'Licenses with Generic Manufacturers. In 2006, we entered into non-exclusive license agreements with thirteen Indian generic manufacturers,granting them the rights to produce and distribute generic versions of tenofovir disoproxil fumarate for the treatment of HIV infection to low income countries around the world, which includes India and many of the low income countries in our GileadAccess Program. The agreements require that the generic manufacturers meet certain national and international regulatory standards and include technology transfers to enable expeditious production of large volumes of high quality generic versions oftenofovir disoproxil fumarate. In addition, these agreements allow for the manufacture of commercial quantities of both active pharmaceutical ingredient and finished product. In 2011, we expanded these non-exclusive license agreements to increasethe number of countries included in the license, and also to include rights to our future pipeline products elvitegravir, an investigational integrase inhibitor; cobicistat, an investigational antiretroviral boosting agent; and Quad, which combinesfour of our HIV medicines in a once-daily single-tablet regimen and is pending FDA approval. To expand access to Viread for the treatment of hepatitis B treatment in developing countries, we also included in these non-exclusive license agreementsthe ability to manufacture and distribute generic versions of tenofovir disoproxil fumarate for the treatment of hepatitis B in the same countries where they are authorized to sell generic versions of tenofovir disoproxil fumarate for HIV.': {},
                                           'Liver Disease': {},
                                           'MARKET FOR REGISTRANT’S COMMON EQUITY, RELATED STOCKHOLDER MATTERS AND ISSUER PURCHASES OF EQUITY SECURITIES': {},
                                           'Maximum Fair Valueof Shares that May YetBe PurchasedUnderthe Program': {},
                                           'Medicines Patent Pool . In 2011, we entered into an agreement with the Pool, an organization that was established by the UnitedNations to increase global access to high-quality, low-cost antiretroviral therapy through the sharing of patents. We granted the Pool a non-exclusive license to identify generic pharmaceutical manufacturers in India who specialize in high-qualityproduction of generic medicines and grant sublicenses to those Indian manufacturers to manufacture and distribute generic versions of our antiretrovirals in the developing world. Sublicensees through the Pool will be free to develop combinationproducts and pediatric formulations of our HIV medicines. We also granted the Pool the right to grant sublicenses to our future pipeline products elvitegravir, cobicistat and Quad to those same generic pharmaceutical manufacturers in India fordistribution in the developing world.': {},
                                           'Merck. In 2006, we entered into an agreement with an affiliate of Merck pursuant to which Gilead and Merck provide Atripla at substantiallyreduced prices to HIV infected patients in developing countries in Africa, the Caribbean, Latin America and Southeast Asia. Under the agreement, we manufacture Atripla using efavirenz supplied by Merck, and Merck handles distribution of the productin the countries covered by the agreement.': {},
                                           'More than 5years': {},
                                           'NOTES TO CONSOLIDATED FINANCIAL STATEMENTS': {},
                                           'NOTES TO CONSOLIDATED FINANCIAL STATEMENTS—': {'2011': '2010',
                                                                                           'Accumulated other comprehensive income': '58200',
                                                                                           'Amortized\xa0Cost': 'Fair '
                                                                                                                'Value',
                                                                                           'Assets:$': '7464485',
                                                                                           'Assets:Debt securities:Certificates of deposit': '—',
                                                                                           'Assets:Debt securities:Corporate debt securities': '—',
                                                                                           'Assets:Debt securities:Money market funds': '7455982',
                                                                                           'Assets:Debt securities:Municipal debt securities': '—',
                                                                                           'Assets:Debt securities:Non-U.S. government securities': '—',
                                                                                           'Assets:Debt securities:Residential mortgage and asset-backed securities': '—',
                                                                                           'Assets:Debt securities:Student loan-backed securities': '—',
                                                                                           'Assets:Debt securities:U.S. government agencies and FDIC guaranteed securities': '—',
                                                                                           'Assets:Debt securities:U.S. treasury securities': '—',
                                                                                           'Assets:Derivatives': '—',
                                                                                           'Assets:Equity securities': '8503',
                                                                                           'Assets:Total debt securities': '7455982',
                                                                                           'Balance, beginning of period': '126516',
                                                                                           'Balance, end of period': '146908',
                                                                                           'Capitalized intangibles': '5227',
                                                                                           'Cumulative foreign currency translation adjustment': '-12496',
                                                                                           'Deferred revenue': '37314',
                                                                                           'Denominator:Effect of dilutive securities:Conversion spread related to the May 2011 Notes': '187',
                                                                                           'Denominator:Effect of dilutive securities:Conversion spread related to the May 2013 Notes': '780',
                                                                                           'Denominator:Effect of dilutive securities:Stock options and equivalents': '14248',
                                                                                           'Denominator:Weighted-average shares of common stock outstanding used in the calculation of basic net income per share attributable to Gilead common stockholders': '774903',
                                                                                           'Denominator:Weighted-average shares of common stock outstanding used in the calculation of diluted net income per share attributable to Gilead common stockholders': '790118',
                                                                                           'Depreciation related': '45223',
                                                                                           'Derivatives designated as hedges:Net gains (losses) reclassified from accumulated OCI into product sales (effective portion)': '-78647',
                                                                                           'Derivatives designated as hedges:Net gains (losses) recognized in interest and other income, net (ineffective portion and amounts excluded from effectiveness testing)': '-17237',
                                                                                           'Derivatives designated as hedges:Net gains recognized in OCI (effective portion)': '1664',
                                                                                           'Derivatives not designated as hedges:Net gains recognized in interest and other income, net': '22084',
                                                                                           'Expected dividend yield': '0',
                                                                                           'Expected term in years:ESPP': '1.4',
                                                                                           'Expected term in years:Stock options': '5.6',
                                                                                           'Expected volatility:ESPP': '30',
                                                                                           'Expected volatility:Stock options': '29',
                                                                                           'Greater than five years but less than ten years': '—',
                                                                                           'Greater than one year but less than five years': '26100',
                                                                                           'Greater than ten years': '7507482',
                                                                                           'Greater than ten years:Total': '9107722',
                                                                                           'Intangibles': '-330184',
                                                                                           'Lapse of statute of limitations': '-3929',
                                                                                           'Less than one year': '1574140',
                                                                                           'Level 1': 'Level 2',
                                                                                           'Liabilities:$': '—',
                                                                                           'Liabilities:Contingent consideration': '—',
                                                                                           'Liabilities:Derivatives': '—',
                                                                                           'May 2011 convertible senior notes': '—',
                                                                                           'May 2013 convertible senior notes': '193231',
                                                                                           'May 2013 convertible senior notes:Total May 2011 and 2013 convertible senior notes': '193231',
                                                                                           'May 2014 convertible senior notes': '107496',
                                                                                           'May 2016 convertible senior notes': '152039',
                                                                                           'May 2016 convertible senior notes:Total May 2014 and 2016 convertible senior notes': '259535',
                                                                                           'Net deferred tax assets': '340589',
                                                                                           'Net operating loss carryforwards': '260907',
                                                                                           'Net unrealized gain (loss) on available-for-sale securities': '-26748',
                                                                                           'Net unrealized gain on cash flow hedges': '97444',
                                                                                           'Numerator:Net income attributable to Gilead': '2803637',
                                                                                           'Other': '-14562',
                                                                                           'Other, net': '58172',
                                                                                           'Other, net:Total deferred tax assets before valuation allowance': '710472',
                                                                                           'Other:Total deferred tax liabilities': '-360674',
                                                                                           'Outside of the United States:France': '587292',
                                                                                           'Outside of the United States:Germany': '370403',
                                                                                           'Outside of the United States:Italy': '392052',
                                                                                           'Outside of the United States:Other European countries': '578792',
                                                                                           'Outside of the United States:Other countries': '652343',
                                                                                           'Outside of the United States:Spain': '498201',
                                                                                           'Outside of the United States:Switzerland': '179582',
                                                                                           'Outside of the United States:Total revenues': '8385385',
                                                                                           'Outside of the United States:Total revenues outside of the United States': '3777042',
                                                                                           'Outside of the United States:United Kingdom': '518377',
                                                                                           'Research and other credit carryforwards': '30350',
                                                                                           'Reserves and accruals not currently deductible': '116564',
                                                                                           'Risk-free interest rate:ESPP': '0.8',
                                                                                           'Risk-free interest rate:Stock options': '2.2',
                                                                                           'Settlements': '-3067',
                                                                                           'Shares': 'Weighted-AverageExercise\xa0'
                                                                                                     'Price',
                                                                                           'Shares:Exercisable, end of year': '41418',
                                                                                           'Shares:Outstanding, beginning of year': '60251',
                                                                                           'Shares:Outstanding, beginning of year:Exercised': '-9175',
                                                                                           'Shares:Outstanding, beginning of year:Expired': '-1117',
                                                                                           'Shares:Outstanding, beginning of year:Forfeited': '-1523',
                                                                                           'Shares:Outstanding, beginning of year:Granted and assumed': '2445',
                                                                                           'Shares:Outstanding, end of year': '50881',
                                                                                           'Shares:Weighted-average grant date fair value of options granted during the year': '12.33',
                                                                                           'Stock-based compensation': '156715',
                                                                                           'Tax positions related to current year:Additions': '21113',
                                                                                           'Tax positions related to current year:Reductions': '—',
                                                                                           'Tax positions related to prior years:Additions': '11171',
                                                                                           'Tax positions related to prior years:Reductions': '-4896',
                                                                                           'United States': '4608343',
                                                                                           'Unremitted foreign earnings': '-15928',
                                                                                           'Valuation allowance': '-9209',
                                                                                           'Valuation allowance:Total deferred tax assets': '701263'},
                                           'No Table Title': {'AmBisome': '330156',
                                                              'Antiviral products:Atripla': '3224518',
                                                              'Antiviral products:Complera/Eviplera': '38747',
                                                              'Antiviral products:Emtriva': '28764',
                                                              'Antiviral products:Hepsera': '144679',
                                                              'Antiviral products:Total antiviral products': '7049716',
                                                              'Antiviral products:Truvada': '2875141',
                                                              'Antiviral products:Viread': '737867',
                                                              'As of December\xa031:Cash, cash equivalents and marketable securities': '9963972',
                                                              'As of December\xa031:Working capital': '11403995',
                                                              'Balance, beginning of period': '80365',
                                                              'Balance, beginning of period:Sales of marketable securities': '-38430',
                                                              'Balance, beginning of period:Total realized and unrealized gains (losses) included in:Interest and other income, net': '6251',
                                                              'Balance, beginning of period:Total realized and unrealized gains (losses) included in:Other comprehensive income (loss), net': '-30376',
                                                              'Balance, beginning of period:Transfers into Level 3': '53883',
                                                              'Balance, end of period': '71693',
                                                              'CONSOLIDATED BALANCE SHEET DATA:Cash, cash equivalents and marketable securities': '9963972',
                                                              'CONSOLIDATED BALANCE SHEET DATA:Convertible senior notes and unsecured senior notes (3)': '7605734',
                                                              'CONSOLIDATED BALANCE SHEET DATA:Other long-term obligations': '147736',
                                                              'CONSOLIDATED BALANCE SHEET DATA:Retained earnings': '1776760',
                                                              'CONSOLIDATED BALANCE SHEET DATA:Total assets (2)': '17303134',
                                                              'CONSOLIDATED BALANCE SHEET DATA:Total stockholders’ equity': '6867349',
                                                              'CONSOLIDATED BALANCE SHEET DATA:Working capital': '11403995',
                                                              'Cash and cash equivalents': '9000954',
                                                              'Foreign earnings at different rates': '-443879',
                                                              'Income before provision for income taxes': '3651004',
                                                              'Letairis': '293426',
                                                              'Long-term marketable securities': '63704',
                                                              'Long-term marketable securities:Total': '9081149',
                                                              'Net unbenefitted stock compensation': '14860',
                                                              'Other': '109057',
                                                              'Other:Provision for income taxes': '861945',
                                                              'Other:Total product sales': '8102359',
                                                              'Ranexa': '320004',
                                                              'Research and other credits': '-32403',
                                                              'Short-term marketable securities': '16491',
                                                              'State taxes, net of federal benefit': '27894',
                                                              'Tax at federal statutory rate': '1277852',
                                                              'Year Ended December\xa031:Cash provided by (used in):Financing activities': '1763569',
                                                              'Year Ended December\xa031:Cash provided by (used in):Investing activities': '3589845',
                                                              'Year Ended December\xa031:Cash provided by (used in):Operating activities': '3639010'},
                                           'Other': {},
                                           'Our results of operations will be adversely affected by current and potential future healthcare reforms.': {},
                                           'Our success will depend to a significant degree on our ability to protect our patents and other intellectual property rights both domestically and internationally. We may not be able to obtaineffective patents to protect our technologies from use by competitors and patents of other companies could require us to stop using or pay for the use of required technology.': {},
                                           'PART I': {},
                                           'PART II': {},
                                           'PART III': {},
                                           'PART IV': {},
                                           'POWER OF ATTORNEY': {},
                                           'PROPERTY, PLANT AND EQUIPMENT': {'Property, plant and equipment, net:Buildings and improvements (including leasehold improvements)': '500040',
                                                                             'Property, plant and equipment, net:Capitalized leased equipment': '10878',
                                                                             'Property, plant and equipment, net:Construction in progress': '60746',
                                                                             'Property, plant and equipment, net:Construction in progress:Subtotal': '983293',
                                                                             'Property, plant and equipment, net:Laboratory and manufacturing equipment': '199693',
                                                                             'Property, plant and equipment, net:Land': '149376',
                                                                             'Property, plant and equipment, net:Land:Total': '774406',
                                                                             'Property, plant and equipment, net:Less accumulated depreciation and amortization (including $10,546 and $10,451 relating to capitalized leased equipment for 2011 and 2010, respectively)': '-358263',
                                                                             'Property, plant and equipment, net:Less accumulated depreciation and amortization (including $10,546 and $10,451 relating to capitalized leased equipment for 2011 and 2010, respectively):Subtotal': '625030',
                                                                             'Property, plant and equipment, net:Office and computer equipment': '211936'},
                                           'PharmaChem Technologies . In 2005, PharmaChem, one of our commercial manufacturing partners, established afacility in The Bahamas to manufacture tenofovir disoproxil fumarate, the active pharmaceutical ingredient in Viread and one of the active pharmaceutical ingredients in Atripla and Truvada, for resource limited countries through a cooperative effortwith PharmaChem and the Grand Bahama Port Authority. This partnership increases manufacturing capacity for our HIV medicines, and improve delivery efficiency, since the medicines are produced in or near the markets where they are needed most.': {},
                                           'Phase 1': {},
                                           'Phase 2': {},
                                           'Product Candidate for the Treatment of Cardiovascular/Metabolic Diseases': {},
                                           'Product Candidates for the Treatment of Cardiovascular/Metabolic Diseases': {},
                                           'Product Candidates for the Treatment of Inflammation/Oncology Diseases': {},
                                           'Product Candidates for the Treatment of Liver Disease': {},
                                           'Product Candidates for the Treatment of Respiratory Diseases': {},
                                           'Product Candidates for theTreatment of HIV': {},
                                           'Product Sales': {'AmBisome': '330156',
                                                             'Antiviral products:Atripla': '3224518',
                                                             'Antiviral products:Complera/Eviplera': '38747',
                                                             'Antiviral products:Emtriva': '28764',
                                                             'Antiviral products:Hepsera': '144679',
                                                             'Antiviral products:Total antiviral products': '7049716',
                                                             'Antiviral products:Truvada': '2875141',
                                                             'Antiviral products:Viread': '737867',
                                                             'Letairis': '293426',
                                                             'Other': '109057',
                                                             'Other products': '109057',
                                                             'Other products:Total product sales': '8102359',
                                                             'Other:Total product sales': '8102359',
                                                             'Ranexa': '320004'},
                                           'Property, Plant and Equipment': {},
                                           'Property, plant and equipment, net:': {},
                                           'QUARTERLY RESULTS OF OPERATIONS': {},
                                           'RESTRUCTURING': {'Balance at December\xa031, 2009': '9689',
                                                             'Balance at December\xa031, 2009:Costs incurred during the period': '2190',
                                                             'Balance at December\xa031, 2009:Costs paid or settled during the period': '-11445',
                                                             'Balance at December\xa031, 2010': '434',
                                                             'Balance at December\xa031, 2010:Costs incurred during the period': '—',
                                                             'Balance at December\xa031, 2010:Costs paid or settled during the period': '-434',
                                                             'Balance at December\xa031, 2011': '—',
                                                             'Costs incurred during the period': '33797',
                                                             'Costs paid or settled during the period': '-24108'},
                                           'Ranexa  is an extended-release tablet for the treatment of chronic angina. We have licensed to Menarini International OperationsLuxembourg SA the rights to Ranexa in territories outside of the United States.': {},
                                           'Research Collaborations': {},
                                           'Research and Development Expenses': {'Research and development': '1229151'},
                                           'Respiratory': {},
                                           'Restricted Stock Units': {'Outstanding, beginning of year': '2649',
                                                                      'Outstanding, beginning of year:Forfeited': '-454',
                                                                      'Outstanding, beginning of year:Granted and assumed': '4215',
                                                                      'Outstanding, beginning of year:Vested': '-587',
                                                                      'Outstanding, end of year': '5823',
                                                                      'Shares': 'Weighted-AverageGrant-DateFair ValuePer '
                                                                                'Share'},
                                           'Royalty Revenues': {'Royalty revenues': '268827'},
                                           'SECURITIES REGISTERED PURSUANT TO SECTION 12 OF THE ACT:': {},
                                           'SECURITIES REGISTERED PURSUANT TO SECTION 12 OF THE ACT: NONE': {},
                                           'SECURITY OWNERSHIP OF CERTAIN BENEFICIAL OWNERS AND MANAGEMENT AND RELATED STOCKHOLDER MATTERS': {},
                                           'SELECTED CONSOLIDATED FINANCIAL DATA—': {},
                                           'STOCK-BASED COMPENSATION': {'Cost of goods sold': '8433',
                                                                        'Income tax effect': '-47325',
                                                                        'Income tax effect:Stock-based compensation expense, net of tax': '145053',
                                                                        'Research and development expenses': '73490',
                                                                        'Selling, general and administrative expenses': '110455',
                                                                        'Selling, general and administrative expenses:Stock-based compensation expense included in total costs and expenses': '192378'},
                                           'Schedule II: Valuation and Qualifying Accounts': {},
                                           'Selling, General and Administrative Expenses': {'Selling, general and administrative': '1241983'},
                                           'Table of Contents': {},
                                           'Truvada': {},
                                           'Truvada  is an oral formulation dosed once a day as part of combination therapy to treat HIVinfection in adults. It is a fixed-dose combination of our antiretroviral medications, Viread and Emtriva.': {},
                                           'U.S. and European Patent Expiration': {},
                                           'UNRESOLVED STAFF COMMENTS': {},
                                           'United States Healthcare Reform': {},
                                           'Viread is an oral formulation of a nucleotide analog reverse transcriptase inhibitor, dosed once a day as part of combination therapy to treatHIV infection in patients 2 years of age and older. Viread is also approved for the treatment of chronic hepatitis B in adults.': {},
                                           'Vistide  is an antiviral injection for the treatment of cytomegalovirus retinitis in adult patients with AIDS.': {},
                                           'We depend on relationships with other companies for sales and marketing performance, development and commercialization of product candidates andrevenues. Failure to maintain these relationships, poor performance by these companies or disputes with these companies could negatively impact our business.': {},
                                           'We face credit risks from our Southern European customers that may adversely affect our results of operations.': {},
                                           'Working Capital': {},
                                           'or': {}}

johnson_johnson_dict = {'CONSOLIDATED BALANCE SHEETS': {'Assets:Current assets:Accounts receivable trade, less allowances for doubtful accounts $248 (2017, $291)': '14098',
                                                       'Assets:Current assets:Assets held for sale (Note 20)': '950',
                                                       'Assets:Current assets:Cash and cash equivalents (Notes\xa01 and 2)': '18107',
                                                       'Assets:Current assets:Inventories (Notes\xa01 and 3)': '8599',
                                                       'Assets:Current assets:Marketable securities (Notes\xa01 and 2)': '1580',
                                                       'Assets:Current assets:Prepaid expenses and other receivables': '2699',
                                                       'Assets:Deferred taxes on income (Note 8)': '7640',
                                                       'Assets:Goodwill (Notes\xa01 and 5)': '30453',
                                                       'Assets:Intangible assets, net (Notes\xa01 and 5)': '47611',
                                                       'Assets:Other assets': '4182',
                                                       'Assets:Property, plant and equipment, net (Notes\xa01 and 4)': '17035',
                                                       'Assets:Total current assets': '46033',
                                                       'Current liabilities:Accounts payable': '7537',
                                                       'Current liabilities:Accrued compensation and employee related obligations': '3098',
                                                       'Current liabilities:Accrued liabilities': '7601',
                                                       'Current liabilities:Accrued rebates, returns and promotions': '9380',
                                                       'Current liabilities:Accrued taxes on income (Note 8)': '818',
                                                       'Current liabilities:Loans and notes payable (Note\xa07)': '2796',
                                                       'Deferred taxes on income (Note 8)': '7506',
                                                       'Employee related obligations (Notes\xa09 and 10)': '9951',
                                                       'Long-term debt (Note\xa07)': '27684',
                                                       'Long-term taxes payable (Note 8)': '8242',
                                                       'Other liabilities': '8589',
                                                       'Shareholders’ equity:94,114': '91714',
                                                       'Shareholders’ equity:Accumulated other comprehensive income (loss) (Note\xa013)': '-15222',
                                                       'Shareholders’ equity:Common stock\xa0— par value $1.00 per share (Note\xa012) (authorized 4,320,000,000\xa0shares; issued 3,119,843,000\xa0shares)': '3120',
                                                       'Shareholders’ equity:Less common stock held in treasury, at cost (Note\xa012) (457,519,000\xa0shares and 437,318,000\xa0shares)': '34362',
                                                       'Shareholders’ equity:Preferred stock\xa0— without par value (authorized and unissued 2,000,000\xa0shares)': '—',
                                                       'Shareholders’ equity:Retained earnings': '106216',
                                                       'Total assets': '152954',
                                                       'Total current liabilities': '31230',
                                                       'Total liabilities': '93202',
                                                       'Total liabilities and shareholders’ equity': '152954',
                                                       'Total shareholders’ equity': '59752'}}

microsoft_dict = {'BALANCE SHEETS': {'Assets:Current assets:Accounts receivable, net of allowance for doubtful accounts of $411 and $377': '29524',
                                     'Assets:Current assets:Cash and cash equivalents': '11356',
                                     'Assets:Current assets:Inventories': '2063',
                                     'Assets:Current assets:Other': '10146',
                                     'Assets:Current assets:Short-term investments': '122463',
                                     'Assets:Current assets:Total cash, cash equivalents, and short-term investments': '133819',
                                     'Assets:Current assets:Total current assets': '175552',
                                     'Assets:Equity investments': '2649',
                                     'Assets:Goodwill': '42026',
                                     'Assets:Intangible assets, net': '7750',
                                     'Assets:Operating lease right-of-use assets': '7379',
                                     'Assets:Other long-term assets': '14723',
                                     'Assets:Property and equipment, net of accumulated depreciation of $35,330 and $29,223': '36477',
                                     'Assets:Total assets': '286556',
                                     'Liabilities and stockholders’ equity:Current liabilities:Accounts payable': '9382',
                                     'Liabilities and stockholders’ equity:Current liabilities:Accrued compensation': '6830',
                                     'Liabilities and stockholders’ equity:Current liabilities:Current portion of long-term debt': '5516',
                                     'Liabilities and stockholders’ equity:Current liabilities:Other': '9351',
                                     'Liabilities and stockholders’ equity:Current liabilities:Short-term income taxes': '5665',
                                     'Liabilities and stockholders’ equity:Current liabilities:Short-term unearned revenue': '32676',
                                     'Liabilities and stockholders’ equity:Current liabilities:Total current liabilities': '69420',
                                     'Liabilities and stockholders’ equity:Deferred income taxes': '233',
                                     'Liabilities and stockholders’ equity:Long-term debt': '66662',
                                     'Liabilities and stockholders’ equity:Long-term income taxes': '29612',
                                     'Liabilities and stockholders’ equity:Long-term unearned revenue': '4530',
                                     'Liabilities and stockholders’ equity:Operating lease liabilities': '6188',
                                     'Liabilities and stockholders’ equity:Other long-term liabilities': '7581',
                                     'Liabilities and stockholders’ equity:Stockholders’ equity:Accumulated other comprehensive loss': '-340',
                                     'Liabilities and stockholders’ equity:Stockholders’ equity:Common stock and paid-in capital – shares authorized 24,000; outstanding 7,643 and\xa07,677': '78520',
                                     'Liabilities and stockholders’ equity:Stockholders’ equity:Retained earnings': '24150',
                                     'Liabilities and stockholders’ equity:Stockholders’ equity:Total liabilities and stockholders’ equity': '286556',
                                     'Liabilities and stockholders’ equity:Stockholders’ equity:Total stockholders’ equity': '102330',
                                     'Liabilities and stockholders’ equity:Total liabilities': '184226'}}

aapl_dict = {'Accrued Warranty and Indemnification': {'Beginning accrued warranty and related costs': 3834.0,
                                                      'Beginning accrued warranty and related costs_Accruals for product warranty': 3973.0,
                                                      'Beginning accrued warranty and related costs_Cost of warranty claims': -4115.0,
                                                      'Ending accrued warranty and related costs': 3692.0},
             'CONSOLIDATED BALANCE SHEETS': {'ASSETS_Current assets_Accounts receivable, net': 23186.0,
                                             'ASSETS_Current assets_Cash and cash equivalents': 25913.0,
                                             'ASSETS_Current assets_Inventories': 3956.0,
                                             'ASSETS_Current assets_Marketable securities': 40388.0,
                                             'ASSETS_Current assets_Other current assets': 12087.0,
                                             'ASSETS_Current assets_Total current assets': 131339.0,
                                             'ASSETS_Current assets_Vendor non-trade receivables': 25809.0,
                                             'ASSETS_Non-current assets_Marketable securities': 170799.0,
                                             'ASSETS_Non-current assets_Other non-current assets': 22283.0,
                                             'ASSETS_Non-current assets_Property, plant and equipment, net': 41304.0,
                                             'ASSETS_Non-current assets_Total non-current assets': 234386.0,
                                             'ASSETS_Total assets': 365725.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Current liabilities_Accounts payable': 55888.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Current liabilities_Commercial paper': 11964.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Current liabilities_Deferred revenue': 7543.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Current liabilities_Other current liabilities': 32687.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Current liabilities_Term debt': 8784.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Current liabilities_Total current liabilities': 116866.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Non-current liabilities_Deferred revenue': 2797.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Non-current liabilities_Other non-current liabilities': 45180.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Non-current liabilities_Term debt': 93735.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Non-current liabilities_Total non-current liabilities': 141712.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Non-current liabilities_Total non-current liabilities_Total liabilities': 258578.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Shareholders’ equity_Accumulated other comprehensive income/(loss)': -3454.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Shareholders’ equity_Common stock and additional paid-in capital, $0.00001 par value 12,600,000 shares authorized; 4,754,986 and 5,126,201 shares issued and outstanding, respectively': 40201.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Shareholders’ equity_Retained earnings': 70400.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Shareholders’ equity_Total shareholders’ equity': 107147.0,
                                             'LIABILITIES AND SHAREHOLDERS’ EQUITY_Total liabilities and shareholders’ equity': 365725.0},
             'CONSOLIDATED STATEMENTS OF CASH FLOWS': {'Cash and cash equivalents, beginning of the year': 20289.0,
                                                       'Cash and cash equivalents, end of the year': 25913.0,
                                                       'Financing activities_Change in commercial paper, net': -37.0,
                                                       'Financing activities_Change in commercial paper, net_Cash used in financing activities': -87876.0,
                                                       'Financing activities_Payments for dividends and dividend equivalents': -13712.0,
                                                       'Financing activities_Payments for taxes related to net share settlement of equity awards': -2527.0,
                                                       'Financing activities_Proceeds from issuance of common stock': 669.0,
                                                       'Financing activities_Proceeds from issuance of term debt, net': 6969.0,
                                                       'Financing activities_Repayments of term debt': -6500.0,
                                                       'Financing activities_Repurchases of common stock': -72738.0,
                                                       'Increase/(Decrease) in cash and cash equivalents': 5624.0,
                                                       'Investing activities_Other': -745.0,
                                                       'Investing activities_Other_Cash generated by/(used in) investing activities': 16066.0,
                                                       'Investing activities_Payments for acquisition of property, plant and equipment': -13313.0,
                                                       'Investing activities_Payments made in connection with business acquisitions, net': -721.0,
                                                       'Investing activities_Proceeds from maturities of marketable securities': 55881.0,
                                                       'Investing activities_Proceeds from non-marketable securities': 353.0,
                                                       'Investing activities_Proceeds from sales of marketable securities': 47838.0,
                                                       'Investing activities_Purchases of marketable securities': -71356.0,
                                                       'Investing activities_Purchases of non-marketable securities': -1871.0,
                                                       'Operating activities_Adjustments to reconcile net income to cash generated by operating activities_Deferred income tax expense/(benefit)': -32590.0,
                                                       'Operating activities_Adjustments to reconcile net income to cash generated by operating activities_Depreciation and amortization': 10903.0,
                                                       'Operating activities_Adjustments to reconcile net income to cash generated by operating activities_Other': -444.0,
                                                       'Operating activities_Adjustments to reconcile net income to cash generated by operating activities_Share-based compensation expense': 5340.0,
                                                       'Operating activities_Changes in operating assets and liabilities_Accounts payable': 9175.0,
                                                       'Operating activities_Changes in operating assets and liabilities_Accounts receivable, net': -5322.0,
                                                       'Operating activities_Changes in operating assets and liabilities_Deferred revenue': -44.0,
                                                       'Operating activities_Changes in operating assets and liabilities_Inventories': 828.0,
                                                       'Operating activities_Changes in operating assets and liabilities_Other current and non-current assets': -423.0,
                                                       'Operating activities_Changes in operating assets and liabilities_Other current and non-current liabilities': 38490.0,
                                                       'Operating activities_Changes in operating assets and liabilities_Other current and non-current liabilities_Cash generated by operating activities': 77434.0,
                                                       'Operating activities_Changes in operating assets and liabilities_Vendor non-trade receivables': -8010.0,
                                                       'Operating activities_Net income': 59531.0,
                                                       'Supplemental cash flow disclosure_Cash paid for income taxes, net': 10417.0,
                                                       'Supplemental cash flow disclosure_Cash paid for interest': 3022.0},
             'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME': {'Net income': 59531.0,
                                                                 'Other comprehensive income/(loss)_Change in foreign currency translation, net of tax effects of $(1), $(77) and $8, respectively': -525.0,
                                                                 'Other comprehensive income/(loss)_Change in unrealized gains/losses on derivative instruments_Adjustment for net (gains)/losses realized and included in net income, net of tax expense/(benefit) of $(104), $475 and $131, respectively': 382.0,
                                                                 'Other comprehensive income/(loss)_Change in unrealized gains/losses on derivative instruments_Adjustment for net (gains)/losses realized and included in net income, net of tax expense/(benefit) of $(104), $475 and $131, respectively_Total change in unrealized gains/losses on derivative instruments, net of tax': 905.0,
                                                                 'Other comprehensive income/(loss)_Change in unrealized gains/losses on derivative instruments_Change in fair value of derivatives, net of tax benefit/(expense) of $(149), $(478) and $(7), respectively': 523.0,
                                                                 'Other comprehensive income/(loss)_Change in unrealized gains/losses on marketable securities_Adjustment for net (gains)/losses realized and included in net income, net of tax expense/(benefit) of $21, $35 and $(31), respectively': 1.0,
                                                                 'Other comprehensive income/(loss)_Change in unrealized gains/losses on marketable securities_Adjustment for net (gains)/losses realized and included in net income, net of tax expense/(benefit) of $21, $35 and $(31), respectively_Total change in unrealized gains/losses on marketable securities, net of tax': -3406.0,
                                                                 'Other comprehensive income/(loss)_Change in unrealized gains/losses on marketable securities_Change in fair value of marketable securities, net of tax benefit/(expense) of $1,156, $425 and $(863), respectively': -3407.0,
                                                                 'Total comprehensive income': 56505.0,
                                                                 'Total other comprehensive income/(loss)': -3026.0},
             'CONSOLIDATED STATEMENTS OF OPERATIONS': {'Cost of sales': 163756.0,
                                                       'Cost of sales_Gross margin': 101839.0,
                                                       'Earnings per share_Basic': 1201.0,
                                                       'Earnings per share_Diluted': 1191.0,
                                                       'Income before provision for income taxes': 72903.0,
                                                       'Net income': 59531.0,
                                                       'Net sales': 265595.0,
                                                       'Operating expenses_Research and development': 14236.0,
                                                       'Operating expenses_Selling, general and administrative': 16705.0,
                                                       'Operating income': 70898.0,
                                                       'Other income/(expense), net': 2005.0,
                                                       'Provision for income taxes': 13372.0,
                                                       'Shares used in computing earnings per share_Basic': 4955377.0,
                                                       'Shares used in computing earnings per share_Diluted': 5000109.0,
                                                       'Total operating expenses': 30941.0},
             'Cash, Cash Equivalents and Marketable Securities': {'Cash': 11575.0,
                                                                  'Level 1 (1)_Money market funds': 8083.0,
                                                                  'Level 1 (1)_Mutual funds': 683.0,
                                                                  'Level 1 (1)_Mutual funds_Subtotal': 683.0,
                                                                  'Level 2 (2)_Certificates of deposit and time deposits': 497.0,
                                                                  'Level 2 (2)_Commercial paper': 910.0,
                                                                  'Level 2 (2)_Corporate securities': 95953.0,
                                                                  'Level 2 (2)_Mortgage- and asset-backed securities': 16686.0,
                                                                  'Level 2 (2)_Mortgage- and asset-backed securities_Subtotal': 170799.0,
                                                                  'Level 2 (2)_Mortgage- and asset-backed securities_Total (3)': 170799.0,
                                                                  'Level 2 (2)_Municipal securities': 756.0,
                                                                  'Level 2 (2)_Non-U.S. government securities': 18045.0,
                                                                  'Level 2 (2)_U.S. Treasury securities': 36875.0,
                                                                  'Level 2 (2)_U.S. agency securities': 1987.0},
             'Commercial Paper': {'Maturities 90 days or less_Proceeds from/(Repayments of) commercial paper, net': 1044.0,
                                  'Maturities greater than 90 days_Proceeds from commercial paper': 14555.0,
                                  'Maturities greater than 90 days_Repayments of commercial paper': -15636.0,
                                  'Maturities greater than 90 days_Repayments of commercial paper_Proceeds from/(Repayments of) commercial paper, net': -1081.0,
                                  'Maturities greater than 90 days_Repayments of commercial paper_Proceeds from/(Repayments of) commercial paper, net_Total change in commercial paper, net': -37.0},
             'Company Stock Performance': {'Apple Inc.': 359.0,
                                           'Dow Jones U.S. Technology Supersector Index': 266.0,
                                           'S&P 500 Index': 192.0,
                                           'S&P Information Technology Index': 275.0},
             'Contractual Obligations': {'Deemed repatriation tax payable': 33589.0,
                                         'Deemed repatriation tax payable_Total': 199622.0,
                                         'Manufacturing purchase obligations (1)': 45200.0,
                                         'Operating leases': 9627.0,
                                         'Other purchase obligations': 7013.0,
                                         'Term debt': 104193.0},
             'Deferred Tax Assets and Liabilities': {'Deferred tax assets_Accrued liabilities and other reserves': 3151.0,
                                                     'Deferred tax assets_Basis of capital assets': 137.0,
                                                     'Deferred tax assets_Deferred cost sharing': 667.0,
                                                     'Deferred tax assets_Deferred revenue': 1141.0,
                                                     'Deferred tax assets_Other': 797.0,
                                                     'Deferred tax assets_Share-based compensation': 513.0,
                                                     'Deferred tax assets_Unrealized losses': 871.0,
                                                     'Deferred tax liabilities_Earnings of foreign subsidiaries': 275.0,
                                                     'Deferred tax liabilities_Earnings of foreign subsidiaries_Other': 501.0,
                                                     'Deferred tax liabilities_Total deferred tax liabilities': 776.0,
                                                     'Net deferred tax assets/(liabilities)': 5834.0,
                                                     'Total deferred tax assets': 6610.0},
             'Derivative Financial Instruments': {'Derivative assets (1)_Foreign exchange contracts': 1274.0,
                                                  'Derivative liabilities (2)_Foreign exchange contracts': 680.0,
                                                  'Derivative liabilities (2)_Interest rate contracts': 1456.0},
             'Earnings Per Share': {'Basic earnings per share': 1201.0,
                                    'Denominator_Effect of dilutive securities': 44732.0,
                                    'Denominator_Weighted-average basic shares outstanding': 4955377.0,
                                    'Denominator_Weighted-average diluted shares': 5000109.0,
                                    'Diluted earnings per share': 1191.0,
                                    'Numerator_Net income': 59531.0},
             'Fair Value': {'Derivative assets (1)_Foreign exchange contracts': 1412.0,
                            'Derivative assets (1)_Interest rate contracts': 218.0,
                            'Derivative liabilities (2)_Foreign exchange contracts': 1260.0,
                            'Derivative liabilities (2)_Interest rate contracts': 303.0,
                            'Gains/(Losses) on derivative instruments_Fair value hedges_Foreign exchange contracts': -168.0,
                            'Gains/(Losses) on derivative instruments_Fair value hedges_Interest rate contracts': -1363.0,
                            'Gains/(Losses) on derivative instruments_Fair value hedges_Interest rate contracts_Total': -1531.0,
                            'Gains/(Losses) reclassified from AOCI into net income – effective portion_Cash flow hedges_Foreign exchange contracts': -482.0,
                            'Gains/(Losses) reclassified from AOCI into net income – effective portion_Cash flow hedges_Interest rate contracts': 1.0,
                            'Gains/(Losses) reclassified from AOCI into net income – effective portion_Cash flow hedges_Interest rate contracts_Total': -481.0,
                            'Gains/(Losses) recognized in OCI – effective portion_Cash flow hedges_Foreign exchange contracts': 682.0,
                            'Gains/(Losses) recognized in OCI – effective portion_Cash flow hedges_Interest rate contracts': 1.0,
                            'Gains/(Losses) recognized in OCI – effective portion_Cash flow hedges_Interest rate contracts_Total': 683.0,
                            'Gains/(Losses) recognized in OCI – effective portion_Net investment hedges_Foreign currency debt': 4.0,
                            'Gains/(Losses) related to hedged items_Fair value hedges_Fixed-rate debt': 1363.0,
                            'Gains/(Losses) related to hedged items_Fair value hedges_Fixed-rate debt_Total': 1530.0,
                            'Gains/(Losses) related to hedged items_Fair value hedges_Marketable securities': 167.0,
                            'Instruments designated as accounting hedges_Foreign exchange contracts': 65368.0,
                            'Instruments designated as accounting hedges_Interest rate contracts': 33250.0,
                            'Instruments not designated as accounting hedges_Foreign exchange contracts': 63062.0},
             'Liquidity and Capital Resources': {'Cash generated by operating activities (2)': 77434.0,
                                                 'Cash generated by/(used in) investing activities': 16066.0,
                                                 'Cash used in financing activities (2)': -87876.0,
                                                 'Cash, cash equivalents and marketable securities (1)': 237100.0,
                                                 'Commercial paper': 11964.0,
                                                 'Property, plant and equipment, net': 41304.0,
                                                 'Total term debt': 102519.0,
                                                 'Working capital': 14473.0},
             'Note 10 – Segment Information and Geographic Data': {'Americas_Net sales': 112093.0,
                                                                   'Americas_Operating income': 34864.0,
                                                                   'Europe_Net sales': 62420.0,
                                                                   'Europe_Operating income': 19955.0,
                                                                   'Greater China_Net sales': 51942.0,
                                                                   'Greater China_Operating income': 19742.0,
                                                                   'Japan_Net sales': 21733.0,
                                                                   'Japan_Operating income': 9500.0,
                                                                   'Long-lived assets_China (1)': 13268.0,
                                                                   'Long-lived assets_China (1)_Other countries': 4073.0,
                                                                   'Long-lived assets_Total long-lived assets': 41304.0,
                                                                   'Long-lived assets_U.S.': 23963.0,
                                                                   'Mac (1)': 25484.0,
                                                                   'Net sales_China (1)': 51942.0,
                                                                   'Net sales_China (1)_Other countries': 115592.0,
                                                                   'Net sales_Total net sales': 265595.0,
                                                                   'Net sales_U.S.': 98061.0,
                                                                   'Other Products (1)(3)': 17417.0,
                                                                   'Other Products (1)(3)_Total net sales': 265595.0,
                                                                   'Other corporate expenses, net': -5108.0,
                                                                   'Other corporate expenses, net_Total operating income': 70898.0,
                                                                   'Research and development expense': -14236.0,
                                                                   'Rest of Asia Pacific_Net sales': 17407.0,
                                                                   'Rest of Asia Pacific_Operating income': 6181.0,
                                                                   'Segment operating income': 90242.0,
                                                                   'Services (2)': 37190.0,
                                                                   'iPad (1)': 18805.0,
                                                                   'iPhone (1)': 166699.0},
             'Note 7 – Comprehensive Income': {'-70': -654.0,
                                               '344': -638.0,
                                               '344_Interest rate contracts': -2.0,
                                               '486': -1952.0,
                                               '486_Unrealized (gains)/losses on marketable securities': -20.0,
                                               '486_Unrealized (gains)/losses on marketable securities_Total amounts reclassified from AOCI': 466.0,
                                               'Unrealized (gains)/losses on derivative instruments_Foreign exchange contracts': 214.0},
             'Operating Expenses': {'Research and development': 14236.0,
                                    'Research and development_Percentage of total net sales': 5.0,
                                    'Selling, general and administrative': 16705.0,
                                    'Selling, general and administrative_Percentage of total net sales': 6.0,
                                    'Total operating expenses': 30941.0,
                                    'Total operating expenses_Percentage of total net sales': 12.0},
             'Other Income/(Expense), Net': {'Interest and dividend income': 5686.0,
                                             'Interest expense': -3240.0,
                                             'Other expense, net': -441.0,
                                             'Other expense, net_Total other income/(expense), net': 2005.0},
             'Other Non-Current Liabilities': {'Long-term taxes payable': 33589.0,
                                               'Long-term taxes payable_Deferred tax liabilities': 426.0,
                                               'Long-term taxes payable_Other non-current liabilities': 11165.0,
                                               'Long-term taxes payable_Total other non-current liabilities': 45180.0},
             'Overview and Highlights': {'Net Sales by Product_Mac (1)': 25484.0,
                                         'Net Sales by Product_Other Products (1)(3)': 17417.0,
                                         'Net Sales by Product_Other Products (1)(3)_Total net sales': 265595.0,
                                         'Net Sales by Product_Services (2)': 37190.0,
                                         'Net Sales by Product_iPad (1)': 18805.0,
                                         'Net Sales by Product_iPhone (1)': 166699.0,
                                         'Net Sales by Reportable Segment_Americas': 112093.0,
                                         'Net Sales by Reportable Segment_Europe': 62420.0,
                                         'Net Sales by Reportable Segment_Greater China': 51942.0,
                                         'Net Sales by Reportable Segment_Japan': 21733.0,
                                         'Net Sales by Reportable Segment_Rest of Asia Pacific': 17407.0,
                                         'Net Sales by Reportable Segment_Rest of Asia Pacific_Total net sales': 265595.0,
                                         'Unit Sales by Product_Mac': 18209.0,
                                         'Unit Sales by Product_iPad': 43535.0,
                                         'Unit Sales by Product_iPhone': 217722.0},
             'Product Performance': {'Net sales': 166699.0,
                                     'Net sales_Percentage of total net sales': 63.0,
                                     'Unit sales': 217722.0},
             'Property, Plant and Equipment, Net': {'Accumulated depreciation and amortization': -49099.0,
                                                    'Accumulated depreciation and amortization_Total property, plant and equipment, net': 41304.0,
                                                    'Land and buildings': 16216.0,
                                                    'Leasehold improvements': 8205.0,
                                                    'Leasehold improvements_Gross property, plant and equipment': 90403.0,
                                                    'Machinery, equipment and internal-use software': 65982.0},
             'Provision for Income Taxes': {'Provision for income taxes': 13372.0,
                                            'Provision for income taxes_Effective tax rate': 183.0},
             'Provision for Income Taxes and Effective Tax Rate': {'Computed expected tax': 17890.0,
                                                                   'Earnings of foreign subsidiaries': -5606.0,
                                                                   'Earnings of foreign subsidiaries_Domestic production activities deduction': -195.0,
                                                                   'Earnings of foreign subsidiaries_Other': 57.0,
                                                                   'Earnings of foreign subsidiaries_Other_Effective tax rate': 183.0,
                                                                   'Earnings of foreign subsidiaries_Other_Provision for income taxes': 13372.0,
                                                                   'Earnings of foreign subsidiaries_Research and development credit, net': -560.0,
                                                                   'Federal_Current': 41425.0,
                                                                   'Federal_Deferred': -33819.0,
                                                                   'Federal_Deferred_Total': 7606.0,
                                                                   'Foreign_Current': 3986.0,
                                                                   'Foreign_Deferred': 1181.0,
                                                                   'Foreign_Deferred_Total': 5167.0,
                                                                   'Impacts of the Act': 1515.0,
                                                                   'Provision for income taxes': 13372.0,
                                                                   'State taxes, net of federal effect': 271.0,
                                                                   'State_Current': 551.0,
                                                                   'State_Deferred': 48.0,
                                                                   'State_Deferred_Total': 599.0},
             'Securities': {'12': 12.0,
                            '12_Fair value of marketable securities': 186837.0,
                            '12_Unrealized losses': -4289.0,
                            'Cash': 7982.0,
                            'Level 1 (1)_Money market funds': 6534.0,
                            'Level 1 (1)_Mutual funds': 711.0,
                            'Level 1 (1)_Mutual funds_Subtotal': 711.0,
                            'Level 2 (2)_Certificates of deposit and time deposits': 772.0,
                            'Level 2 (2)_Commercial paper': 1494.0,
                            'Level 2 (2)_Corporate securities': 125688.0,
                            'Level 2 (2)_Mortgage- and asset-backed securities': 20888.0,
                            'Level 2 (2)_Mortgage- and asset-backed securities_Subtotal': 194714.0,
                            'Level 2 (2)_Mortgage- and asset-backed securities_Total': 194714.0,
                            'Level 2 (2)_Municipal securities': 850.0,
                            'Level 2 (2)_Non-U.S. government securities': 7868.0,
                            'Level 2 (2)_U.S. Treasury securities': 36989.0,
                            'Level 2 (2)_U.S. agency securities': 1659.0},
             'Securities registered pursuant to Section 12(b) of the Act:': {},
             'Segment Operating Performance': {'Net sales': 112093.0,
                                               'Net sales_Percentage of total net sales': 42.0},
             'Selected Financial Data': {'Cash dividends declared per share': 272.0,
                                         'Earnings per share_Basic': 1201.0,
                                         'Earnings per share_Diluted': 1191.0,
                                         'Net income': 59531.0,
                                         'Net sales': 265595.0,
                                         'Non-current portion of term debt': 93735.0,
                                         'Other non-current liabilities': 45180.0,
                                         'Shares used in computing earnings per share_Basic': 4955377.0,
                                         'Shares used in computing earnings per share_Diluted': 5000109.0,
                                         'Total assets': 365725.0,
                                         'Total cash, cash equivalents and marketable securities': 237100.0},
             'Share-Based Compensation': {'Cost of sales': 1010.0,
                                          'Research and development': 2668.0,
                                          'Selling, general and administrative': 1662.0,
                                          'Selling, general and administrative_Total share-based compensation expense': 5340.0},
             'Term Debt': {'2013 debt issuance of $17.0 billion_Fixed-rate 2.400% – 3.850% notes': 2023.0,
                           '2013 debt issuance of $17.0 billion_Floating-rate notes': 2000.0,
                           '2014 debt issuance of $12.0 billion_Fixed-rate 2.100% – 4.450% notes': 2019.0,
                           '2014 debt issuance of $12.0 billion_Floating-rate notes': 2019.0,
                           '2015 debt issuances of $27.3 billion_Fixed-rate 0.350% – 4.375% notes': 2019.0,
                           '2015 debt issuances of $27.3 billion_Floating-rate notes': 2019.0,
                           '2016 debt issuances of $24.9 billion_Fixed-rate 1.100% – 4.650% notes': 2019.0,
                           '2016 debt issuances of $24.9 billion_Floating-rate notes': 2019.0,
                           '2017 debt issuances of $28.7 billion_Fixed-rate 0.875% – 4.300% notes': 2019.0,
                           '2017 debt issuances of $28.7 billion_Floating-rate notes': 2019.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Fixed-rate 1.800% notes': 2019.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Fixed-rate 2.000% notes': 2020.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Fixed-rate 2.400% notes': 2023.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Fixed-rate 2.750% notes': 2025.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Fixed-rate 3.000% notes': 2027.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Fixed-rate 3.750% notes': 2047.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Fixed-rate 3.750% notes_Total term debt': 104193.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Hedge accounting fair value adjustments': -1456.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Less Current portion of term debt': -8784.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Less Current portion of term debt_Total non-current portion of term debt': 93735.0,
                           'First quarter 2018 debt issuance of $7.0 billion_Unamortized premium/(discount) and issuance costs, net': -218.0},
             'Total': {'12': 12.0,
                       '12_Fair value of marketable securities': 110276.0,
                       '12_Unrealized losses': -782.0},
             'Uncertain Tax Positions': {'Beginning balances': 8407.0,
                                         'Beginning balances_Decreases related to expiration of statute of limitations': -39.0,
                                         'Beginning balances_Decreases related to settlements with taxing authorities': -756.0,
                                         'Beginning balances_Decreases related to tax positions taken during a prior year': -2212.0,
                                         'Beginning balances_Increases related to tax positions taken during a prior year': 2431.0,
                                         'Beginning balances_Increases related to tax positions taken during the current year': 1824.0,
                                         'Ending balances': 9694.0}}


tsla_normalized = {'Balance Sheet_Assets_Current Assets_Accounts Receivable_Allowances for Doubtful Accounts': np.nan,
                   'Balance Sheet_Assets_Current Assets_Accounts Receivable_Gross Accounts Receivable': np.nan,
                   'Balance Sheet_Assets_Current Assets_Accounts Receivable_Net Accounts Receivable': 1370570.0,
                   'Balance Sheet_Assets_Current Assets_Accounts Receivable_Other Receivables': np.nan,
                   'Balance Sheet_Assets_Current Assets_Assets Held-for-sale': np.nan,
                   'Balance Sheet_Assets_Current Assets_Cash and Short Term Investments_Cash and Cash Equivalents_Cash and Cash Equivalents': 3685618.0,
                   'Balance Sheet_Assets_Current Assets_Cash and Short Term Investments_Cash and Cash Equivalents_Cash and Due from Banks': np.nan,
                   'Balance Sheet_Assets_Current Assets_Cash and Short Term Investments_Cash and Cash Equivalents_Interest-bearing Deposits in Banks and Other Financial Institutions': np.nan,
                   'Balance Sheet_Assets_Current Assets_Cash and Short Term Investments_Cash and Cash Equivalents_Other Cash and Cash Equivalents': np.nan,
                   'Balance Sheet_Assets_Current Assets_Cash and Short Term Investments_Cash and Cash Equivalents_Restricted Cash Current': 590770.0,
                   'Balance Sheet_Assets_Current Assets_Cash and Short Term Investments_Cash and Short Term Investments': 16667.0,
                   'Balance Sheet_Assets_Current Assets_Cash and Short Term Investments_Marketable Securities Current': 16667.0,
                   'Balance Sheet_Assets_Current Assets_Deferred Tax Assets, Current': np.nan,
                   'Balance Sheet_Assets_Current Assets_Income Taxes Receivable, Current': np.nan,
                   'Balance Sheet_Assets_Current Assets_Inventory, Net': 3113446.0,
                   'Balance Sheet_Assets_Current Assets_Other Assets, Current': np.nan,
                   'Balance Sheet_Assets_Current Assets_Prepaid Expense, Current': 365671.0,
                   'Balance Sheet_Assets_Current Assets_Total Assets, Current': 8306308.0,
                   'Balance Sheet_Assets_Non Current Assets_Deferred Tax Assets Non Current': 6357841.0,
                   'Balance Sheet_Assets_Non Current Assets_Intangible Assets_Goodwill': 68159.0,
                   'Balance Sheet_Assets_Non Current Assets_Intangible Assets_Intangible Assets, Net (Excluding Goodwill)': 282492.0,
                   'Balance Sheet_Assets_Non Current Assets_Intangible Assets_Total Intangible Assets': 724658.0,
                   'Balance Sheet_Assets_Non Current Assets_Marketable Securities Non Current': np.nan,
                   'Balance Sheet_Assets_Non Current Assets_Operating Lease Right-of-use Assets': np.nan,
                   'Balance Sheet_Assets_Non Current Assets_Other Non Current Assets': 571657.0,
                   'Balance Sheet_Assets_Non Current Assets_Property, Plant and Equipment_Accumulated Depreciation and Amortization': -2699098.0,
                   'Balance Sheet_Assets_Non Current Assets_Property, Plant and Equipment_Gross Property, Plant and Equipment': np.nan,
                   'Balance Sheet_Assets_Non Current Assets_Property, Plant and Equipment_Property, Plant and Equipment, Net': 11330077.0,
                   'Balance Sheet_Assets_Non Current Assets_Restricted Cash Non Current': 398219.0,
                   'Balance Sheet_Assets_Non Current Assets_Total Non Current Assets': 29739614.0,
                   'Balance Sheet_Assets_Operating Lease Vehicles, Net': 2089758.0,
                   'Balance Sheet_Assets_Solar Energy Systems, Leased and to Be Leased, Net': 6271396.0,
                   'Balance Sheet_Assets_Total Assets': 29739614.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Accounts Payable, Current": 3404451.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Accrued Income Taxes": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Accrued Liabilities, Current": 2094253.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Current Deferred Revenues": 1621165.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Current Portion of Promissory Notes Issued to Related Parties": 100000.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Customer Deposits": 792601.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Employee-related Liabilities, Current": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Income Taxes Payable": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Long-term Debt, Current Maturities": 11971371.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Operating Lease, Liability, Current": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Other Current Liabilities": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Resale Value Guarantees": 502840.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Short-Term Debt": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Current Liabilities_Total Current Liabilities": 9992136.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Non Current Liabilities_Accrued Income Taxes, Noncurrent": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Non Current Liabilities_Deferred Revenue, Noncurrent": 406661.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Non Current Liabilities_Deferred Tax Liabilities": -1843855.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Non Current Liabilities_Liability, Defined Benefit Plan, Noncurrent": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Non Current Liabilities_Long-Term Unearned Revenue": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Non Current Liabilities_Long-term Debt, Noncurrent Maturities": 9403672.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Non Current Liabilities_Operating Lease, Liability, Noncurrent": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Non Current Liabilities_Other Liabilities, Noncurrent": 2710403.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Non Current Liabilities_Total Long-Term Liabilities": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Total Liabilities": 23426010.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Accumulated Other Comprehensive Income (Loss)": -14532.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Common Stock and Additional Paid in Capital_Additional Paid in Capital": 10249120.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Common Stock and Additional Paid in Capital_Common Stock, Value, Issued": 173.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Common Stock and Additional Paid in Capital_Common Stocks, Including Additional Paid in Capital": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Common Stock and Additional Paid in Capital_Weighted Average Number Diluted Shares Outstanding Adjustment": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Common Stock and Additional Paid in Capital_Weighted Average Number of Shares Outstanding, Basic": 170525.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Common Stock and Additional Paid in Capital_Weighted Average Number of Shares Outstanding, Diluted": 170525.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Deferred Stock Compensation": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Minority Interest": 31129975.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Preferred Stock, Value, Issued": 173.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Retained Earnings (Accumulated Deficit)": -5317832.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Stockholders' Equity Attributable to Parent": 4923243.0,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Treasury Stock, Value": np.nan,
                   "Balance Sheet_Liabilities and Shareholders' Equity_Total Liabilities and Shareholders' Equity": 29739614.0,
                   'Cash Flow Statement_Financing Activities_Acquisitions of Property and Equipment Included in Liabilities': 249141.0,
                   'Cash Flow Statement_Financing Activities_Cash and Cash Equivalents and Restricted Cash, Beginning of Period': 3964959.0,
                   'Cash Flow Statement_Financing Activities_Cash and Cash Equivalents and Restricted Cash, End of Period': 4276388.0,
                   'Cash Flow Statement_Financing Activities_Collateralized Lease (Repayments) Borrowings': -559167.0,
                   'Cash Flow Statement_Financing Activities_Common Stock and Debt Issuance Costs': -14973.0,
                   'Cash Flow Statement_Financing Activities_Distributions Paid to Noncontrolling Interests in Subsidiaries': -227304.0,
                   'Cash Flow Statement_Financing Activities_Effect of Exchange Rate Changes on Cash and Cash Equivalents and Restricted Cash': -22700.0,
                   'Cash Flow Statement_Financing Activities_Estimated Fair Value of Facilities Under Build-To-Suit Leases': 94445.0,
                   'Cash Flow Statement_Financing Activities_Net Cash Provided by (Used in) Financing Activities': 573755.0,
                   'Cash Flow Statement_Financing Activities_Net Increase in Cash and Cash Equivalents and Restricted Cash': 311429.0,
                   'Cash Flow Statement_Financing Activities_Payments for Buy-Outs of Noncontrolling Interests in Subsidiaries': -5957.0,
                   'Cash Flow Statement_Financing Activities_Payments for Settlements of Warrants': -11.0,
                   'Cash Flow Statement_Financing Activities_Principal Payments on Capital Leases': -180805.0,
                   'Cash Flow Statement_Financing Activities_Proceeds From Exercises of Stock Options and Other Stock Issuances': 295722.0,
                   'Cash Flow Statement_Financing Activities_Proceeds From Investments by Noncontrolling Interests in Subsidiaries': 437134.0,
                   'Cash Flow Statement_Financing Activities_Proceeds From Issuances of Common Stock in Public Offerings': 400175.0,
                   'Cash Flow Statement_Financing Activities_Proceeds From Issuances of Convertible and Other Debt': 6176173.0,
                   'Cash Flow Statement_Financing Activities_Proceeds From Issuances of Warrants': 52883.0,
                   'Cash Flow Statement_Financing Activities_Proceeds From Settlement of Convertible Note Hedges': 287213.0,
                   'Cash Flow Statement_Financing Activities_Purchases of Convertible Note Hedges': -204102.0,
                   'Cash Flow Statement_Financing Activities_Repayments of Borrowings Issued to Related Parties': -100000.0,
                   'Cash Flow Statement_Financing Activities_Repayments of Convertible and Other Debt': -5247057.0,
                   'Cash Flow Statement_Financing Activities_Shares Issued in Connection With Business Combinations and Assumed Vested Awards': 10528.0,
                   'Cash Flow Statement_Investing Activities_Business Combinations, Net of Cash Acquired': -17912.0,
                   'Cash Flow Statement_Investing Activities_Maturities of Short-Term Marketable Securities': 16667.0,
                   'Cash Flow Statement_Investing Activities_Net Cash Provided by (Used in) Investing Activities': -2337428.0,
                   'Cash Flow Statement_Investing Activities_Purchases of Property and Equipment Excluding Capital Leases, Net of Sales': -2100724.0,
                   'Cash Flow Statement_Investing Activities_Purchases of Solar Energy Systems, Leased and to Be Leased': -218792.0,
                   'Cash Flow Statement_Operating Activities_Net Cash Provided by (Used in) Operating Activities': 2146309.0,
                   'Cash Flow Statement_Operating Activities_Net Loss': -1062582.0,
                   'Income Statement_Costs and Expenses_Cost of Goods and Services Sold': 31593244.0,
                   'Income Statement_Costs and Expenses_Costs and Expenses': np.nan,
                   'Income Statement_Costs and Expenses_Operating Expenses_Depreciation, Depletion and Amortization, Nonproduction': 1901050.0,
                   'Income Statement_Costs and Expenses_Operating Expenses_EBITDA': np.nan,
                   'Income Statement_Costs and Expenses_Operating Expenses_Other Operating Expenses': np.nan,
                   'Income Statement_Costs and Expenses_Operating Expenses_Research and Development Expense': 1460370.0,
                   'Income Statement_Costs and Expenses_Operating Expenses_Restructuring and Other': 135233.0,
                   'Income Statement_Costs and Expenses_Operating Expenses_Selling, General and Administrative_General and Administrative Expense': np.nan,
                   'Income Statement_Costs and Expenses_Operating Expenses_Selling, General and Administrative_Marketing Expense': np.nan,
                   'Income Statement_Costs and Expenses_Operating Expenses_Selling, General and Administrative_Selling and Marketing Expense': np.nan,
                   'Income Statement_Costs and Expenses_Operating Expenses_Selling, General and Administrative_Selling, General and Administrative': 2834491.0,
                   'Income Statement_Costs and Expenses_Operating Expenses_Total Operating Expenses': 4430094.0,
                   'Income Statement_Costs and Expenses_Provision for Loan, Lease, and Other Losses': np.nan,
                   'Income Statement_Income (Loss) before Income Taxes, Noncontrolling Interest': np.nan,
                   'Income Statement_Income Tax Expense (Benefit)': 57837.0,
                   'Income Statement_Net Income (Loss)': -1062582.0,
                   'Income Statement_Net Income (Loss) Available to Common Stockholders, Basic': np.nan,
                   'Income Statement_Net Income Loss Attributable to Noncontrolling (Minority) Interest': np.nan,
                   'Income Statement_Non-Operating Income (Expense)_Earnings Before Interest and Taxes (EBIT)': np.nan,
                   'Income Statement_Non-Operating Income (Expense)_Interest Expense': -663071.0,
                   'Income Statement_Non-Operating Income (Expense)_Interest Income (Expense), Net': np.nan,
                   'Income Statement_Non-Operating Income (Expense)_Interest and Dividend Income': 24533.0,
                   'Income Statement_Non-Operating Income (Expense)_Non-Operating Income (Expense)': 21866.0,
                   'Income Statement_Non-Operating Income (Expense)_Other Nonoperating Income (Expense)': np.nan,
                   'Income Statement_Operating Income (Loss) / EBIT': np.nan,
                   'Income Statement_Preferred Stock Dividends, Income Statement Impact': np.nan,
                   'Income Statement_Revenues_Automotive Leasing': 883461.0,
                   'Income Statement_Revenues_Automotive Sales': 17631522.0,
                   'Income Statement_Revenues_Energy Generation and Storage': 1555244.0,
                   'Income Statement_Revenues_Net Sales': 39976251.0,
                   'Income Statement_Revenues_Noninterest Income': np.nan,
                   'Income Statement_Revenues_Services and Other': 1391041.0,
                   'Income Statement_Undistributed Earnings (Loss) Allocated to Participating Securities, Basic': np.nan}