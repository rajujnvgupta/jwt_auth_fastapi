# schemaa helps to serialize and also convert mangodb format json to our UI needed

def userEntity(db_item) -> dict:
    return {
        "id":   str(db_item["_id"]),
        "username": db_item["username"],
        "email": db_item["email"]
    }

def listOfUserEntity(db_item_list) -> list:
    list_user_entity = []
    for item in db_item_list:
        list_user_entity.append(userEntity(item))

    return list_user_entity