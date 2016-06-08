package com.pythonanywhere.sedi.foodster.models;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 * Created by Dominik on 2016-05-10.
 */
public class ResponseWrapper {

    private int responseCode;
    private String JSONAsString;

    public ResponseWrapper(int responseCode, String JSONAsString){
        this.responseCode = responseCode;
        this.JSONAsString = JSONAsString;
    }

    public int getResponseCode(){
        return responseCode;
    }

    public JSONArray getJSONArray() throws JSONException {
        return new JSONArray(JSONAsString.toString());
    }

    public JSONObject getJSONObject() throws JSONException {
        return  new JSONObject(JSONAsString.toString());
    }

    public String toString(){
        return JSONAsString;
    }


}
