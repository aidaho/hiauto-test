#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import asyncio
import re
from enum import Enum, auto

import aiofiles

# Menu configuration
MENU: dict[str, float] = {
    "americano": 1.51,
    "espresso": 1.27,
    "latte": 2.13,
    "macchiato": 3.39,
    "tea": 1.75,
    "cookie": 0.50,
}
DRINKS: set[str] = {"americano", "espresso", "latte", "macchiato", "tea"}
COOKIE_PRICE = MENU["cookie"]

class OrderAction(Enum):
    ADD = auto()
    REMOVE = auto()
    FINALIZE = auto()
    UNKNOWN = auto()

class ConversationAI:
    def __init__(self) -> None:
        self.employee_queue: asyncio.Queue[str] = asyncio.Queue()
        self.guest_queue: asyncio.Queue[str] = asyncio.Queue()
        self.order: list[str] = []
        self.upsell_attempted: bool = False
        self.conversation_active: bool = True
        self.employee_queue = asyncio.Queue()
        self.guest_queue = asyncio.Queue()

    async def guest_agent(self, filepath: str) -> None:
        """Process guest messages and handle conversation flow"""
        # Send initial greeting through employee
        await self.employee_queue.put("Welcome to our coffee shop. What can I get you?")

        done = False
        async with aiofiles.open(filepath) as f:
            async for msg in f:
                employee_msg = await self.employee_queue.get()
                print(f"Employee: {employee_msg}")

                # Process guest response
                print(f"Guest: {msg.strip()}")
                await self.guest_queue.put(msg.strip())

                # Check if conversation should continue
                if msg.lower().strip().startswith("that's all"):
                    done = True
                    break

        # Send final response if needed
        if not done:
            await self.guest_queue.put("That's all")

    async def employee_agent(self) -> None:
        """Handle employee responses and order logic"""
        while self.conversation_active:
            guest_msg = await self.guest_queue.get()
            action, item = self.parse_guest_message(guest_msg)

            if action == OrderAction.ADD:
                if item:  # only add valid items
                    self.order.append(item)
                response = self.handle_upsell() or "Would you like anything else?"
            elif action == OrderAction.REMOVE:
                self.order.remove(item)
                response = "Would you like anything else?"
            elif action == OrderAction.FINALIZE:
                valid_items = [item for item in self.order if item in MENU]
                total = sum(MENU[item] for item in valid_items)
                response = f"Your total is ${total:.2f}. Thank you and have a nice day!"
                self.conversation_active = False
                # Clear queues to prevent hanging
                while not self.guest_queue.empty():
                    await self.guest_queue.get()
                print(f"Employee: {response}")
            else:
                response = "I don't understand."

            await self.employee_queue.put(response)

    def handle_upsell(self) -> str | None:
        """Check if we should upsell cookies and return upsell message if appropriate"""
        if (any(item in DRINKS for item in self.order) and
            "cookie" not in self.order and
            not self.upsell_attempted):
            self.upsell_attempted = True
            return f"Would you like to add a cookie for ${COOKIE_PRICE:.2f}?"
        return None

    def parse_guest_message(self, message: str) -> tuple[OrderAction, str]:
        """Parse guest message into action and item"""
        message = message.lower().strip()
        if message.startswith("that's all"):
            return (OrderAction.FINALIZE, "")
        # Handle cookie responses with possible punctuation
        if message.startswith(("yes, please", "no, thank you")):
            if message.startswith("yes, please"):
                return (OrderAction.ADD, "cookie")
            return (OrderAction.ADD, "")  # Empty action to trigger "anything else"

        parts = message.split()
        item = parts[-1].rstrip('?.')
        if re.match(r".*(?<!don't)\s+(want|like).*", message):
            return (OrderAction.ADD, item) if item in MENU else (OrderAction.ADD, "")
        elif re.match(r".*don't\s+(want|like).*", message):  # noqa:RET505
            return (OrderAction.REMOVE, item) if item in MENU else (OrderAction.ADD, "")

        return (OrderAction.UNKNOWN, "")


async def main() -> None:
    parser = argparse.ArgumentParser(description='HiAuto Coffee Shop Conversation Simulator')
    parser.add_argument('file', nargs=1, help='Input file with guest messages')
    args = parser.parse_args()

    ai = ConversationAI()

    tasks = [
        asyncio.create_task(ai.guest_agent(args.file[0])),
        asyncio.create_task(ai.employee_agent()),
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
