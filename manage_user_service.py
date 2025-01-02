import dbus

# Connect to the user session bus
session_bus = dbus.SessionBus()

# Access the systemd user instance
systemd = session_bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')

def list_user_managed_units():
    try:
        # Retrieve all units for the current user session
        units = manager.ListUnits()

        # Display only units managed by the current user
        print(f"{'UNIT':<40} {'LOAD STATE':<15} {'ACTIVE STATE':<15}")
        print("=" * 70)
        for unit in units:
            unit_name, load_state, active_state = unit[0], unit[2], unit[3]
            # Check if the unit type ends in .service, .timer, or .socket, indicating it's user-managed
            if unit_name.endswith(('.service', '.timer', '.socket')):
                print(f"{unit_name:<40} {load_state:<15} {active_state:<15}")

    except dbus.exceptions.DBusException as e:
        print(f"Failed to list user-managed units: {e}")

if __name__ == "__main__":
    list_user_managed_units()
