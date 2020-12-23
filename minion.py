# awarder.py - steam-awarder - maxtheaxe
# code taken in part from my previous selenium/python projects
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller as cda # makes it easier on inexperienced users
import twint as tw # unofficial twit api of sorts, so ppl don't have to set up dev stuff
from playsound import playsound # for notifying users; optional
from datetime import datetime
import random
import signal
import os
import inspect
import sys

# set path to chrome driver for packaging purposes
# ref: https://stackoverflow.com/questions/41030257/is-there-a-way-to-bundle-a-binary-file-such-as-chromedriver-with-a-single-file
current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0]))

# launch() - launch sequence to get driver started, bring to login page
def launch(headless = False, signin_details = None):
	driver = start_driver(headless) # start the driver and store it (will be returned)
	# open paypal login page, to get setup for onetouch checkout later
	driver.get("https://www.paypal.com/us/signin")
	# wait until page loads
	try: # loook for cookie button as indicator of load
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.element_to_be_clickable((By.ID, 'acceptAllButton')))
		# accept cookies so we can actually stay logged in
		driver.find_element_by_id("acceptAllButton").click()
	except: # page didn't load in a reasonable amount of time
		print("\n\tError: Page didn't load in a reasonable amount of time; try again.\n")
		driver.quit() # close selenium driver
		sys.exit() # close python program
	if (signin_details == None):
		# notify user they have to sign in
		print("\n\tPlease sign into PayPal via the browser window (click 'Log In').")
		# wait for user input to resume
		input("\n\tAfterwards, hit [Enter] (in this window) to continue...")
		# open paypal onetouch login page, set up for faster checkout later
	driver.get("https://www.paypal.com/us/webapps/mpp/one-touch-checkout")
	# wait until onetouch setup page loads
	try: # look for activate button as indicator of load
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.element_to_be_clickable(
			(By.XPATH, "//a[contains(text(), 'Activate One Touch')]")))
		# click activate button
		driver.find_element_by_xpath("//a[contains(text(), 'Activate One Touch')]").click()
	except: # page didn't load in a reasonable amount of time
		print("\n\tError: Page didn't load in a reasonable amount of time; try again.\n")
		driver.quit() # close selenium driver
		sys.exit() # close python program
	if (signin_details == None):
		# notify user they have to sign in again to activate onetouch
		print("\n\tPlease activate PayPal Onetouch via the browser window (click 'Activate').")
		# wait for user prompt to resume
		input("\n\tAfterwards, hit [Enter] (in this window) to continue...")
	# wait until onetouch setup page loads
	try: # look for my account button as indicator of load
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.element_to_be_clickable(
			(By.XPATH, "//a[contains(text(), 'Go to My Account')]")))
	except: # page didn't load in a reasonable amount of time
		print("\n\tError: Page didn't load in a reasonable amount of time; try again.\n")
		driver.quit() # close selenium driver
		sys.exit() # close python program
	# navigate off of paypal page to make user feel more comfortable
	driver.get("https://discountmoneystore.com/")
	return driver # return driver so it can be stored and used later

# start_driver() - starts the webdriver (dls if needed) and returns it
def start_driver(headless = False):
	# if chromedriver doesn't exist, dl it, then set path to it
	# chromedriver = os.path.join(current_folder,"chromedriver.exe")
	cda.install()
	# setup webdriver settings
	options = webdriver.ChromeOptions()
	# add ublock origin to reduce impact, block stuff
	# options.add_extension("ublock_origin.crx")
	# other settings
	options.headless = headless # headless or not, passed as arg
	options.add_experimental_option('excludeSwitches', ['enable-logging']) # chrome only maybe
	# make window size bigger
	# options.add_argument("--window-size=1600,1200")
	# , executable_path = cda.get_chromedriver_path()
	return webdriver.Chrome(options = options)

# get_formatted_time() - return datetime with necessary twint formatting
# ref: https://www.programiz.com/python-programming/datetime/current-time
def get_formatted_time():
	now = datetime.now()
	current_time = now.strftime("%Y-%m-%d %H:%M:%S")
	return current_time

# restock_checker() - checks @tendmoney twitter for restock notifications
def restock_checker(last_check_time = "2020-12-23 14:20:00"):
	# config settings for twitter scraping (via twint)
	cfg = tw.Config()
	cfg.Username = "tendmoney"
	cfg.Since = last_check_time # tweets since last check
	# cfg.Limit = 1 # max num tweets
	cfg.Search = "DiscountMoneyStore.com" # search term
	# run twitter search with given filters
	search_results = tw.run.Search(cfg)
	# check num results (if not None, a restock has happened!)
	if (search_results != None): # restock happened -- some results
		return True, last_check_time
	else: # no restock happened -- None results
		# only get new time if necessary to save (a tiny bit of) time
		return False, get_formatted_time()

# buy_money() - buys biggest quantity of money above given threshold, unless given target
# ref: https://stackoverflow.com/a/23078602/4513452
def buy_money(driver, lowest_amount = None, product_ids = None, specific_target = None):
	# hard-coded product ids (decreasing); should update dynamically on program start
	product_ids = [40, 77, 79, 48, 83, 70]
	# try purchases in decreasing order
	for i in range(len(product_ids)): # need to add lower threshold
		# create product add url according to iteration number
		product_url = ("https://discountmoneystore.com/?add-to-cart=" + str(product_ids[i]))
		# navigate to given url
		driver.get(product_url)
		# check if a product was successfully added
		try:
			# check if there is a product button with text "Added"
			driver.find_element_by_xpath("//a[contains(text(), 'Added')]")
		except NoSuchElementException: # handle exception for xpath fail
			if (i == (len(product_ids) - 1)): # if already looped over all denoms
				# if there aren't six out of stock products listed, alert user
				if (len(driver.find_elements_by_class_name("outofstock")) != 6):
					# user needs to take over (probably issues with page loading)
					# might add proper waits later if it's a major issue
					# play notification sound 15 times
					for i in range(15):
						playsound(manual_notify.mp3)
			continue # wasn't found, must already be sold out--skip to next-highest
		# navigate to cart/checkout area
		driver.get("https://discountmoneystore.com/cart/")
	return

# load_from_file() - loads a list of links from file
# ref: https://codippa.com/how-to-read-a-file-line-by-line-into-a-list-in-python/
def load_from_file(file_name):
	# open file in read mode
	with open(file_name, 'r') as filename:
		# read file content into list broken up by line (w/o newline chars)
		lines = [line.rstrip() for line in filename]
	return lines # return list of urls

def main():
	# display title
	print("\n\t--- Discount Money Bot by Max ---\n")
	# warn users about using program
	input("\tWarning: Use this program at your own risk!\n\t(press Enter to continue)\n\n\t")
	# start driver, have user sign into paypal onetouch, then save driver
	driver = launch()
	# define starting parameters
	last_check_time = get_formatted_time()
	restock_status = False
	# keep checking twitter until a restock happens
	print("\n\tChecking for restocks...\n")
	# while (restock_status != True):
	# 	restock_status, last_check_time = restock_checker(last_check_time)
	# 	time.sleep(20) # wait twenty seconds
	# restock happened, indicate as such in cli
	print("\n\tRestock Alert! Navigating to buy page...\n")
	# go buy discount money
	buy_money(driver)
	# # create the driver (browser window) and keep track of it
	# main_driver = launch()
	# # if external list of URLs is provided
	# if (args.urlfile != None):
	# 	# then draw from there
	# 	url_list = load_from_file(args.urlfile)
	# 	# loop over list of URLs
	# 	for i in range(len(url_list)):
	# 		# if a custom page limit is provided
	# 		if (args.pagelimit != None):
	# 			# give awards to each in list with custom limit
	# 			run_with_target(main_driver, url_list[i], max_pages = args.pagelimit)
	# 		else: # otherwise use default
	# 			# give awards to each in list
	# 			run_with_target(main_driver, url_list[i])
	# # otherwise, get links to reviews pages from user input
	# else:
	# 	while True:
	# 		# if a custom page limit is provided
	# 		if (args.pagelimit != None):
	# 			run_with_target(main_driver, max_pages = args.pagelimit)
	# 		else: # otherwise use default
	# 			run_with_target(main_driver)

if __name__ == '__main__':
	main()