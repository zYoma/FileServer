from string import Template

from pydantic import BaseSettings


class CommonConfig(BaseSettings):
    file_list: Template = Template("file_list_v1_$user_id")
    get_current_user: Template = Template("get_current_user_$token")
    search_files: Template = Template("search_files_$user_id$path$extension$order_by$limit")
    revision_files: Template = Template("revision_files_$user_id$path$limit")


all_keys = CommonConfig()
