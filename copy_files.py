import os
def assemble_files(file_paths, output_file):
    """
    Reads content from each file in file_paths and writes them sequentially
    into output_file with headers indicating the source file.
    
    :param file_paths: List of file paths to copy
    :param output_file: Path to the assembled output file
    """
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for path in file_paths:
            if not os.path.exists(path):
                print(f"⚠️ File not found: {path}")
                continue

            out_f.write(f"\n\n# ====== Begin of {path} ======\n\n")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                out_f.write(content)
            out_f.write(f"\n\n# ====== End of {path} ======\n\n")
    
    print(f"✅ All files assembled into {output_file}")


if __name__ == "__main__":
    # Example usage:
    files_to_copy = ["app.py",   
             "pages/login.py",
             "pages/register.py",
             "backend/auth/auth_manager.py",
             "frontend/components/auth/registration_form.py",

            # "backend/db/base.py",
        # "backend/auth/session_manager.py",          
          # "backend/utils/security/password_utils.py",
          # "backend/utils/widget_manager.py",
        #   "backend/utils/error_handler.py",
        #   "backend/utils/session_cleaner.py",
          # "backend/utils/validators.py",
            #"backend/models/db_models.py", 
           # "backend/models/domain_models.py", 
           # "backend/models/data_transfer.py", 
        #    "backend/services/user_service.py", 
       # "frontend/components/navigation/__init__.py",
       # "frontend/components/navigation/sidebar.py",
       # "frontend/components/navigation/header.py",

       # "pages/project_setup.py",
        # "backend/services/project_service.py", 
#"backend/db/repositories/project_repo.py",
       #  "frontend/components/forms/project_forms.py",
        
         # "frontend/pages/templates_manager.py",
      #  "frontend/components/tabs/task_library.py",
      # "frontend/components/tabs/resource_library.py",
      #  "frontend/components/tabs/template_association.py",
        # "backend/services/user_task_service.py", 
        # "backend/services/template_service.py", 
        # "backend/services/resource_service.py", 
         #"backend/db/repositories/task_repo.py",
         #"backend/db/repositories/resource_repo.py",

        #"frontend/pages/generate_schedule.py",
         # "backend/services/scheduling_service.py",
          # "backend/db/repositories/schedule_repo.py",


    ]
    assemble_files(files_to_copy, "assembled_code1.txt")