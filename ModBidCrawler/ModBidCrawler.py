from urllib2 import urlopen, URLError
from bs4 import BeautifulSoup
import re
import json
import time
import pprint

def processType(stu_type):
    stu_grp = {}
    stu_type = stu_type.lower()
    if 'returning' in stu_type:
        grp = {}
        index = stu_type.find('returning') + len('returning')
        type = stu_type[stu_type.find('[',index):stu_type.find(']',index)+1]
        grp = {'Returning':{'P'}}
        stu_grp.update(grp)
    if 'new' in stu_type:
           grp = {}
           index = stu_type.find('new') + len('new')
           type = stu_type[stu_type.find('[',index):stu_type.find(']',index)+1]
           grp = {'New':{'P'}}
           stu_grp.update(grp)
    if 'nus' in stu_type:
       grp = {}
       index = stu_type.find('nus') + len('nus')
       type = stu_type[stu_type.find('[',index):stu_type.find(']',index)+1]
       if not stu_grp: # empty
           if 'p' in type and 'g' in type:
               grp = {'Returning':{'P','G'},'New':{'P','G'}}
           elif 'p' in type:
               grp = {'Returning':{'P'},'New':{'P'}}
           elif 'g' in type:
              grp = {'Returning':{'G'},'New':{'G'}}
       else:
           if 'p' in type and 'g' in type:
               if 'Returning' not in stu_grp:
                  grp = {'Returning':{'P','G'}} 
               else:
                  stu_grp['Returning'].update({'P','G'})
               if 'New' not in stu_grp:
                   grp = {'New':{'P','G'}} 
               else:
                   stu_grp['New'].update({'P','G'})
           elif 'p' in type:
               if 'Returning' not in stu_grp:
                  grp = {'Returning':{'P'}} 
               else:
                  stu_grp['Returning'].update('P')
               if 'New' not in stu_grp:
                   grp = {'New':{'P'}} 
               else:
                   stu_grp['New'].update({'P'})
           elif 'g' in type:
               if 'Returning' not in stu_grp:
                  grp = {'Returning':{'G'}} 
               else:
                  stu_grp['Returning'].update({'G'})
               if 'New' not in stu_grp:
                   grp = {'New':{'G'}} 
               else:
                   stu_grp['New'].update({'G'})
       stu_grp.update(grp)
    return stu_grp

def aggregateData(quota,num_bidders,lowest_bid,lowest_succ_bid,highest_bid):
    return {'Quota': quota,'No of bidders':num_bidders,'Lowest bid':lowest_bid,'Lowest successful bid':lowest_succ_bid,'Highest bid': highest_bid}
                                                                            
def crawl(link):
    page = urlopen(link)
    soup = BeautifulSoup(page)
    round = str(soup.select('body > h2')[0].string).split(' ')[-1][0:-1]
    rows =  soup.select('body > table > tr')
    info = {}
    index = 1
    curr_mod_info = {}
    while index < len(rows):
        row = rows[index]
        module = str(row.select('td:nth-of-type(1) p')[0].string)
        group = str(row.select('td:nth-of-type(2) p')[0].string) # the if statement seems redundant
        if row.select('td:nth-of-type(1)')[0].get('colspan') == None: # either new module/group
            # Step 1 -- Aggregate common data in every row of the table
            quota = str(row.select('td:nth-of-type(3) p')[0].string)
            num_of_bidders = str(row.select('td:nth-of-type(4) p')[0].string)
            lowest_bid = str(row.select('td:nth-of-type(5) p')[0].string)
            lowest_succ_bid = str(row.select('td:nth-of-type(6) p')[0].string)
            highest_bid = str(row.select('td:nth-of-type(7) p')[0].string)
            bid_info = aggregateData(quota,num_of_bidders,lowest_bid,lowest_succ_bid,highest_bid)
            # end of step 1
            # Step 2 -- Make the second half of the json format file depending on the student type
            faculty = str(row.select('td:nth-of-type(8) p')[0].string)
            student_type = str(row.select('td:nth-of-type(9) p')[0].text)
            student_type_grps = processType(student_type)
            secHalf = {}
            for type in student_type_grps:
                data ={}
                dummy = {};
                for acc in student_type_grps[type]:
                    dummy[acc] = bid_info
                pri_data = {faculty:dummy}
                data = {type:pri_data}
                secHalf.update(data) 
            # end of step 2
            # Step 3 --  Check if Module/Group already exist in info list
            if module not in info:
                # make a new module
                curr_grp = {group:secHalf}
                curr_mod_info[module] = curr_grp
                info.update(curr_mod_info)
            else:
                if group not in info[module]:
                    # make a new grp
                    curr_grp = {group:secHalf}
                    info[module].update(curr_grp)
        index += 1
        while index < len(rows) and rows[index].select('td:nth-of-type(1)')[0].get('colspan') != None: # additional info to existing module/grp data
            row = rows[index]
            # Step 1 -- Aggregate common data in every row of the table
            quota = str(row.select('td:nth-of-type(2) p')[0].string)
            num_of_bidders = str(row.select('td:nth-of-type(3) p')[0].string)
            lowest_bid = str(row.select('td:nth-of-type(4) p')[0].string)
            lowest_succ_bid = str(row.select('td:nth-of-type(5) p')[0].string)
            highest_bid = str(row.select('td:nth-of-type(6) p')[0].string)
            bid_info = aggregateData(quota,num_of_bidders,lowest_bid,lowest_succ_bid,highest_bid)
            # end of step 1
            # Step 2 -- Make the second half of the json format file depending on the student type
            faculty = str(row.select('td:nth-of-type(7) p')[0].string)
            student_type = str(row.select('td:nth-of-type(8) p')[0].text)
            student_type_grps = processType(student_type)
            secHalf = {}
            for type in student_type_grps:
                data ={}
                dummy = {};
                for acc in student_type_grps[type]:
                    dummy[acc] = bid_info
                pri_data = {faculty:dummy}
                data = {type:pri_data}
                secHalf.update(data) 
            # end of step 2
            #pp = pprint.PrettyPrinter(indent = 4,depth=6,width=100)
            #pp.pprint(secHalf)
            # push into the dict
            for type in secHalf:
                if type in info[module][group]:
                    for fac in secHalf[type]:
                        if fac in info[module][group][type]:
                              for acc in secHalf[type][fac]:
                                  if acc not in info[module][group][type][fac]:
                                      info[module][group][type][fac][acc] = secHalf[type][fac][acc]
                        else:
                            info[module][group][type].update(secHalf[type])
                else:
                    info[module][group].update(secHalf)
            index += 1
    return {'Round':round,'Info':info}
    #print(round)
    #pp = pprint.PrettyPrinter(indent = 4,depth=6,width=100)
    #pp.pprint(info)

def getLink(raw_link):
    if(re.compile('^./').search(raw_link)):
        url = 'http://www.nus.edu.sg/cors/'
        raw_link = url + raw_link[2:]
    return raw_link

def parser():
    print('Crawling...')
    start_time = time.time()
    try:
        page = urlopen("http://www.nus.edu.sg/cors/archive.html")
        soup = BeautifulSoup(page)
        # Only looks for bidding after Acad Yr 10/11 
        links = soup.find_all('a',href=re.compile('^./Archive/201[1-4]'),text=re.compile('Bidding'));# text=re.compile('Bidding') for info frm round 1A to 3
        bid_info = []
        # curr acad yr's bidding stats
        newList = ["./Reports/successbid_1A_20132014s1.html","./Reports/successbid_1B_20132014s1.html","./Reports/successbid_1C_20132014s1.html","./Reports/successbid_2A_20132014s1.html","./Reports/successbid_2B_20132014s1.html","./Reports/successbid_3A_20132014s1.html","./Reports/successbid_3B_20132014s1.html"]
        index = 0
        round = []
        annual_bid = {}
        while index < len(newList):
            round.append(crawl(getLink(newList[index])))
            index += 1
        annual_bid.update({'Year': '2013/2014','Semester':'1', 'Bid': round })
        bid_info.append(annual_bid) 

        index = 0
        round = []
        annual_bid = {}
        while index < len(links):
            link = links[index]
            annual_bid = {}
            round = [];
            curr_acadYr = link.parent.parent.parent.parent.parent.parent.parent.select('tr td span.whitepaneltitle')[0].string.split(' ')[-1]
            curr_sem = link.parent.parent.parent.select('tr td.whitepaneltitle')[0].string.split(' ')[-1]
            while index < len(links) and curr_sem == links[index].parent.parent.parent.select('tr td.whitepaneltitle')[0].string.split(' ')[-1] and curr_acadYr == links[index].parent.parent.parent.parent.parent.parent.parent.select('tr td span.whitepaneltitle')[0].string.split(' ')[-1]:
                round.append(crawl(getLink(links[index]['href'])))
                index += 1
            annual_bid.update({'Year':str(curr_acadYr),'Semester':str(curr_sem), 'Bid': round })
            bid_info.append(annual_bid) 
    except URLError:
        pass
    print('Crawling took {} seconds').format(time.time() - start_time)
    with open('filename.json', 'w') as outfile:
        #json.dump(bid_info, outfile)
        #outfile.write(json.dumps(bid_info,sort_keys = True,indent=4))
        outfile.write(json.dumps(bid_info))
if __name__ == '__main__' : parser()