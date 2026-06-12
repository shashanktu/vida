from .logger import get_logger
from .llm import get_azure_response
from .preprocess import clean_yaml_output
from .script_validator import validate_yaml,validate_hcl
logger = get_logger(__name__)
def create_yaml_scripts(instructions, max_retries=3, language="yaml"):
    logger.info("[create_yaml_scripts] Called.")
    print("[create_yaml_scripts] Called.")
    attempt = 0
    while attempt < max_retries:
        try:
            response = get_azure_response(instructions)
            logger.info(f"[create_scripts] Azure response received. Attempt {attempt+1}")
            clean_yaml = clean_yaml_output(response)
            logger.info("[create_scripts] Clean YAML output generated.")
            logger.info("Validating the generated script")
            if language == "yaml":
                is_valid, error = validate_yaml(clean_yaml)
                if is_valid:
                    logger.info(" Script is valid.")
                    return True, clean_yaml, None
                else:
                    logger.error(f" Script is invalid. {error}")
                attempt += 1
                if attempt < max_retries:
                    logger.info(f"Retrying to generate valid YAML (Attempt {attempt+1}/{max_retries})...")
            elif language == "hcl":
                is_valid, error = validate_hcl(clean_yaml)
                if is_valid:
                    logger.info("Script is valid.")
                    return True, clean_yaml, None
                else:
                    logger.error(f"Script is invalid. {error}")
                attempt += 1
                if attempt < max_retries:
                    logger.info(f"Retrying to generate valid HCL (Attempt {attempt+1}/{max_retries})...")
        except Exception as e:
            logger.error(f"[create_scripts] Azure Error: {str(e)}", exc_info=True)
            print(f"Azure Error: {str(e)}")
            return f"Azure Error: {str(e)}"
    logger.error(f"[create_scripts] Failed to generate valid {language} script after {max_retries} attempts.")
    return False ,None,f"Failed to generate valid {language} script after {max_retries} attempts."