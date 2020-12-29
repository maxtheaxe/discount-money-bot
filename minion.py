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
from datetime import datetime, timedelta
import time
import random
import signal
import os
import inspect
import sys
import random

# set path to chrome driver for packaging purposes
# ref: https://stackoverflow.com/questions/41030257/is-there-a-way-to-bundle-a-binary-file-such-as-chromedriver-with-a-single-file
current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0]))

# collect_details() - collects user's checkout details
def collect_details():
	user_details = []
	user_details.append(input("\tEnter your first name for checkout purposes\n\t(press Enter to continue)\n\n\t"))
	user_details.append(input("\n\tEnter your last name for checkout purposes\n\t(press Enter to continue)\n\n\t"))
	user_details.append(input("\n\tEnter your venmo username for checkout purposes\n\t(press Enter to continue)\n\n\t"))
	user_details.append(input("\n\tEnter your email for checkout purposes\n\t(press Enter to continue)\n\n\t"))
	# show details as confirmation
	print("\n\tPlease confirm your details:\n")
	print("\n\tFirst Name: ", user_details[0], "\n")
	print("\n\tLast Name: ", user_details[1], "\n")
	print("\n\tVenmo Username: ", user_details[2], "\n")
	print("\n\tEmail Address: ", user_details[3], "\n")
	check = input("\tAre these details correct?\n\t(press 'Y' to continue, or 'N' to retry, followed by [Enter])\n\n\t")
	# well? are they right or not?
	if (check.lower() == 'y'):
		# they were correct, so save 'em
		return user_details
	else:
		# they were wrong, re-collect 'em
		return collect_details()

# launch() - launch sequence to get driver started, bring to login page
def launch(headless = False, signin_details = None):
	driver = start_driver(headless) # start the driver and store it (will be returned)
	# open paypal login page, to get setup for onetouch checkout later
	driver.get("https://www.paypal.com/us/signin")
	# wait until page loads (no need if not logging in automatically)
	try: # loook for cookie button as indicator of load
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.element_to_be_clickable((By.ID, 'acceptAllButton')))
		# accept cookies so we can actually stay logged in
		driver.find_element_by_id("acceptAllButton").click()
	except: # page didn't load in a reasonable amount of time
		print("\n\tError: Page didn't load in a reasonable amount of time; try again.\n")
		# (no need if not logging in automatically)
		# driver.quit() # close selenium driver
		# sys.exit() # close python program
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
	now = datetime.now() # time now
	half_hour = ( now - timedelta(minutes = 30) ) # time 30 min ago
	# returns half hour ago to accommodate for failed checks
	# (bc twint behaves as if none found if check failed)
	current_time = half_hour.strftime("%Y-%m-%d %H:%M:%S")
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
		print("\n\tNo restock tweet found since ", last_check_time, "\n")
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
		try: # look for twitter button as indicator of load
			wait = WebDriverWait(driver, 15)
			element = wait.until(EC.element_to_be_clickable(
			(By.XPATH, "//a[@href='https://twitter.com/tendmoney']")))
			# check if there is a product button with text "Added"
			driver.find_element_by_xpath("//a[contains(text(), 'Clear Cart')]")
		except NoSuchElementException: # handle exception for xpath fail
			if (i == (len(product_ids) - 1)): # if already looped over all denoms
				# if there aren't six out of stock products listed, alert user
				if (len(driver.find_elements_by_class_name("outofstock")) != 6):
					# user needs to take over (probably issues with page loading)
					# might add proper waits later if it's a major issue
					manual_takeover() # swap to manual mode
					return
			continue # wasn't found, must already be sold out--skip to next-highest
		# navigate to cart/checkout area
		driver.get("https://discountmoneystore.com/cart/")
		return

# checkout() - check out with money
def checkout(driver, user_details):
	# wait until checkout page loads
	try: # look for twitter button as indicator of load
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.element_to_be_clickable(
			(By.XPATH, "//a[@href='https://twitter.com/tendmoney']")))
	except: # page didn't load in a reasonable amount of time
		manual_takeover() # swap to manual mode
	# fill out checkout details
	driver.find_element_by_id("billing_first_name").send_keys(user_details[0]) # first name
	driver.find_element_by_id("billing_last_name").send_keys(user_details[1]) # last name
	driver.find_element_by_id("ak_venmo").send_keys(user_details[2]) # venmo username
	driver.find_element_by_id("billing_email").send_keys(user_details[3]) # email address
	# switch to popup/new page (https://stackoverflow.com/a/29052586/4513452)
	# try: # look for clear cart button as indicator of load
	# 	wait = WebDriverWait(driver, 15)
	# 	# not working even though i swear it's right
	# 	# element = wait.until(EC.element_to_be_clickable(
	# 	# 	(By.XPATH, '/html/body/div[1]/div/div[1]/div')))
	# 	element = wait.until(EC.element_to_be_clickable(
	# 		(By.XPATH, "//a[contains(text(), 'Clear Cart')]")))
	# except: # page didn't load in a reasonable amount of time
	# 	manual_takeover() # swap to manual mode
	# driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div').click() # click pay
	time.sleep(10) # i have no idea why this ^ shit doesn't work, f this
	# this is so janky lol don't tell anyone
	driver.find_element_by_id("billing_email").click() # click email address
	driver.find_element_by_id("billing_email").send_keys(Keys.TAB) # tab over to paypal
	ActionChains(driver).key_down(Keys.RETURN).key_up(Keys.RETURN).perform() # hit enter
	# driver.find_element_by_xpath("/html").send_keys(Keys.RETURN) # hit enter on paypal
	time.sleep(10)
	# try: # look for overlay as indicator of load
	# 	wait = WebDriverWait(driver, 15)
	# 	element = wait.until(EC.element_to_be_clickable(
	# 		(By.XPATH, "//a[contains(text(), 'Click to Continue')]")))
	# except: # page didn't load in a reasonable amount of time
	# 	manual_takeover() # swap to manual mode
	main_window_handle = driver.window_handles[0] # get main window handle for later
	paypal_window_handle = driver.window_handles[1] # get paypal popup handle
	# print("pp handle: ", paypal_window_handle)
	driver.switch_to.window(paypal_window_handle) # focus on popup
	try: # look for final payment button as indicator of load
		wait = WebDriverWait(driver, 25)
		element = wait.until(EC.element_to_be_clickable(
			(By.ID, "payment-submit-btn")))
	except: # page didn't load in a reasonable amount of time
		manual_takeover() # swap to manual mode
	# testing
	# pp = driver.find_element_by_id("payment-submit-btn") # .click()
	# print("pp: ", pp) # dont want to actually check out during testing
	# real checkout
	driver.find_element_by_id("payment-submit-btn").click()
	return

# manual_takeover() - for giving user control (just hangs program indefinitely lol)
def manual_takeover():
	count = 0
	while(True):
		count += 1
		# do nothing, should have completed
		if count == 1:
			print("\n\tError: Something went wrong; take over from here.\n")
			# play notification sound 15 times
			for i in range(15):
				# playsound(manual_notify.mp3)
				print("manual takeover needed")
	return

def main():
	# display title
	print("\n\t--- Discount Money Bot by Max ---\n")
	# warn users about using program
	input("\tWarning: Use this program at your own risk!\n\t(press Enter to continue)\n\t")
	# collect users details
	user_details = collect_details()
	# start driver, have user sign into paypal onetouch, then save driver
	driver = launch()
	# define starting parameters
	last_check_time = get_formatted_time()
	restock_status = False
	# keep checking twitter until a restock happens
	print("\n\tChecking for restocks...\n")
	while (restock_status != True):
		restock_status, last_check_time = restock_checker(last_check_time)
		sleep_time = (2 + random.randint(0,15)) # sleep for anywhere between 20 and 35s
		time.sleep(30) # wait thirty seconds
	# restock happened, indicate as such in cli
	print("\n\tRestock Alert! ", last_check_time, " Navigating to buy page...\n")
	# go buy discount money
	buy_money(driver)
	print("\n\tAdded some money to cart. Checking out...\n")
	# go check out
	checkout(driver, user_details)
	count = 0
	while(True):
		count += 1
		# do nothing, should have completed
		if count == 1:
			print("\n\tSuccessfully checked out. Please check window to verify...\n\t" +
		"(you can close it afterwards)\n")

if __name__ == '__main__':
	main()