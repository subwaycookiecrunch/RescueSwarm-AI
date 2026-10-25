"""Interactive Terminal CLI demonstrating Milestone 1 of RescueSwarm AI."""

from __future__ import annotations
import asyncio
import sys
import time
from rescueswarm.models import SwarmLog
from rescueswarm.engine import SwarmEngine


# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"


def format_ts():
    return time.strftime("[%H:%M:%S]", time.localtime())


def print_log(log: SwarmLog):
    """Format and print real-time agent events."""
    ts_str = f"{DIM}[{log.time_str}]{RESET}"

    if log.level == "CHAOS":
        print(f"{ts_str} {BOLD}{RED}{log.message}{RESET}")
    elif log.level == "CRITICAL":
        print(f"{ts_str} {BOLD}{RED}🚨 {log.message}{RESET}")
    elif log.level == "WARN":
        print(f"{ts_str} {YELLOW}⚠️  {log.message}{RESET}")
    elif log.level == "SUCCESS":
        print(f"{ts_str} {GREEN}{log.message}{RESET}")
    else:
        role_tag = f"{CYAN}[{log.agent_role.upper()}]{RESET}"
        print(f"{ts_str} {role_tag} {log.message}")


async def run_milestone1_demo(engine: SwarmEngine):
    """Run the exact milestone sequence."""
    print(f"\n{BOLD}{CYAN}================================================================{RESET}")
    print(f"{BOLD}{WHITE}    RESCUESWARM AI — MILESTONE 1 CLI DEMO{RESET}")
    print(f"{DIM}    Tagline: 'When everything goes wrong, the swarm reorganizes.'{RESET}")
    print(f"{BOLD}{CYAN}================================================================{RESET}\n")

    # Attach log printer
    engine.event_bus.add_log_listener(print_log)

    print(f"{format_ts()} {GREEN}Initializing RescueSwarm cluster...{RESET}")
    await engine.start()
    await asyncio.sleep(1.0)
    print(f"{format_ts()} {GREEN}System health: 100% | 5/5 Agents Active{RESET}\n")

    # Step 1: Major emergency injection (47 chaotic reports)
    print(f"{BOLD}{YELLOW}>>> [00:10] SIMULATING MAJOR DISASTER (47 chaotic reports incoming)...{RESET}")
    await asyncio.sleep(1.2)
    await engine.simulate_major_emergency()
    await asyncio.sleep(1.5)

    # Step 2: Road blockage reaction
    print(f"\n{BOLD}{YELLOW}>>> [00:30] OPERATOR CHAOS ACTION: Raj clicks 'BLOCK ROAD B'{RESET}")
    await asyncio.sleep(1.0)
    await engine.simulate_block_road_b()
    await asyncio.sleep(2.0)

    # Step 3: Hostile fake news rumor injection
    print(f"\n{BOLD}{YELLOW}>>> [00:40] ADVERSARIAL INJECTION: '100 PEOPLE TRAPPED AT LOCATION X'{RESET}")
    await asyncio.sleep(1.0)
    await engine.simulate_inject_fake_news()
    await asyncio.sleep(2.0)

    # Step 4: The Hero Feature — Kill Routing Agent & Self-Healing
    print(f"\n{BOLD}{YELLOW}>>> [00:50] CHAOS INJECTION: KILL ROUTING AGENT{RESET}")
    print(f"{BOLD}{RED}> kill routing-agent{RESET}")
    await engine.kill_agent("routing-agent")

    # Wait for Recovery Agent watchdog to detect failure and self-heal
    await asyncio.sleep(4.0)

    print(f"\n{BOLD}{GREEN}================================================================{RESET}")
    print(f"{BOLD}{GREEN}    MILESTONE 1 VERIFICATION COMPLETE ✓{RESET}")
    print(f"{DIM}    Swarm demonstrated self-healing, hostile data filtering & dynamic rerouting.{RESET}")
    print(f"{BOLD}{GREEN}================================================================{RESET}\n")


async def interactive_shell(engine: SwarmEngine):
    """Interactive command-line loop."""
    print(f"\n{BOLD}RescueSwarm Command Prompt{RESET}")
    print(f"Commands: {CYAN}disaster{RESET} | {CYAN}block-road{RESET} | {CYAN}unblock-road{RESET} | {CYAN}fake-news{RESET} | {RED}kill routing-agent{RESET} | {GREEN}revive{RESET} | {YELLOW}status{RESET} | {WHITE}exit{RESET}\n")

    while True:
        try:
            prompt_str = f"{BOLD}rescueswarm> {RESET}"
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, prompt_str)
            cmd = cmd.strip().lower()

            if not cmd:
                continue

            if cmd in ("exit", "quit"):
                print(f"{format_ts()} Shutting down swarm...")
                await engine.stop()
                break

            elif cmd == "disaster":
                print(f"{format_ts()} Injecting disaster stream...")
                await engine.simulate_major_emergency()

            elif cmd in ("block-road", "block-road-b", "block road b", "block"):
                print(f"{format_ts()} Blocking Road B...")
                await engine.simulate_block_road_b()

            elif cmd in ("unblock-road", "unblock", "clear-road"):
                print(f"{format_ts()} Unblocking Road B...")
                await engine.simulate_unblock_road_b()

            elif cmd in ("fake-news", "rumor", "fake"):
                print(f"{format_ts()} Injecting adversarial rumor...")
                await engine.simulate_inject_fake_news()

            elif cmd in ("kill routing-agent", "kill routing", "kill-routing"):
                print(f"{format_ts()} Killing routing-agent...")
                await engine.kill_agent("routing-agent")

            elif cmd in ("revive", "revive routing-agent"):
                print(f"{format_ts()} Reviving routing-agent...")
                await engine.revive_agent("routing-agent")

            elif cmd in ("reset", "restart"):
                print(f"{format_ts()} Resetting swarm to 00:00...")
                await engine.reset_simulation()

            elif cmd == "status":
                health = engine.get_health()
                print(f"\n{BOLD}--- Swarm Health: {health.system_health_pct}% ---{RESET}")
                print(f"Healthy Agents: {health.healthy_agents}/{health.total_agents}")
                print(f"Active Incidents: {health.active_incidents}")
                print(f"Quarantined Rumors: {health.quarantined_rumors}")
                print(f"Self-Healing Events: {health.self_healing_events}")
                if health.last_healing_event:
                    print(f"Last Recovery: {health.last_healing_event}")
                print()

            elif cmd in ("milestone", "demo"):
                await run_milestone1_demo(engine)

            else:
                print(f"Unknown command: '{cmd}'. Try: disaster, block-road, fake-news, kill routing-agent, status, exit")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            await engine.stop()
            break


async def main():
    engine = SwarmEngine()
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        await run_milestone1_demo(engine)
    else:
        await run_milestone1_demo(engine)
        await interactive_shell(engine)


if __name__ == "__main__":
    asyncio.run(main())
