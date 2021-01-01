# [Discount Money Bot](https://github.com/maxtheaxe/discount-money-bot.git) # 

> [...] finding great deals, and maximizing your money doesn’t have to be so complicated. And that 
> everyone deserves a fair shot at striking it rich. We’ll send you an invitation to join Tend when 
> we launch, and we’ll enter you for a chance to win a bathtub full of money. For swimming, saving, 
> or spending—your money, your call. 

Snag the best deals from [@tendmoney](https://twitter.com/tendmoney)'s [popup shop](https://discountmoneystore.com/)

## Technologies ##

- [Python 3.6+](https://www.python.org/downloads/)
- [Selenium](https://selenium-python.readthedocs.io)
- [Twint](https://pypi.org/project/twint/)

## Installation ##

1. **Clone the Repository**:
    - *Linux*: 
        ```bash
        export SOURCE="https://github.com/maxtheaxe/discount-money-bot.git"
       
        git clone --recurse-submodules "${SOURCE}"
       
        cd ./discount-money-bot
        ```
    - *Windows-10*:
        ```powershell
        ...
        ```

1. **Install Dependencies**:
    - *Linux*:
        ```bash
        python3 -m pip install --requirement Dependencies
        ```
    - *Windows-10*:
        ```powershell
        python -m pip install --requirement Dependencies
        ```

## Usage
* Run `minion.py` (looks for restocks since the time it was launched)
* Type in checkout details at launch
* Log into PayPal in the browser when prompted
* let the bot handle the rest (see [demo video](https://youtu.be/YHFMMb7r71c) for normal operation)

## Disclaimers & Notes
* Primarily: be considerate⁠—just buy something once
* Use at your own risk
* Make sure your default PayPal payment method has enough money/credit available to make the purchase
* Could _definitely_ be cleaned up, open to pull requests
