"""
Standalone runner that ONLY checks the Cool Shit Premium Collection
password lock - separate from the main tracker's SITES list, so this
can run on its own aggressive 1-minute schedule without slowing down
or being slowed down by anything else.
"""

from sites import coolshit_password_watch
from notify import notify_priority_products

SITE_NAME = coolshit_password_watch.SITE_NAME


def main():
    print(f"Checking {SITE_NAME}...")
    try:
        products = coolshit_password_watch.get_current_products()
    except Exception as e:
        print(f"  Failed: {e}")
        return

    if products:
        print(f"  UNLOCKED - sending alert!")
        notify_priority_products(SITE_NAME, products)
    else:
        print("  Still locked (or already alerted)")


if __name__ == "__main__":
    main()
