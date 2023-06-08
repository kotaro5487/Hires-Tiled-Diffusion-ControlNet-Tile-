import launch

if not launch.is_installed("webuiapi"):
    launch.run_pip("install webuiapi", "requirements for ")