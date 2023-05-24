def cmd_reload_source_files(self, args):
    "Reload source files if they have been modified"
    module_names = args.strip().split()
    if module_names:
        for module_name in module_names:
            module_path = os.path.join(self.coder.root, module_name)
            if os.path.isfile(module_path):
                self.coder.reload_module_by_source_file(module_path)
                self.io.tool(f"Reloaded module {module_name}")
            else:
                self.io.tool_error(f"Error: File '{module_name}' does not exist.")
    else:
        self.io.tool(
            "No module names provided. Please provide a space-separated list of module names to reload.")
