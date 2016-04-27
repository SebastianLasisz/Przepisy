package com.pythonanywhere.sedi.foodster.models;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;


public class JSONfunctions {

    public static JSONArray getJSONfromURL(String stringUrl) {
        InputStream in = null;
        String result = "";
//        JSONObject jArray = null;
        JSONArray jArray = null;
        HttpURLConnection connection = null;

        try {
            URL url = new URL(stringUrl);
            connection = (HttpURLConnection) url.openConnection();
            in = new BufferedInputStream(connection.getInputStream());

            BufferedReader br = new BufferedReader(new InputStreamReader(in));
            StringBuilder stringJSON = new StringBuilder();
            String line;

            while ((line = br.readLine()) != null) {
                stringJSON.append(line).append('\n');
            }
//            jArray = new JSONObject(stringJSON.toString());,
            jArray = new JSONArray(stringJSON.toString());




        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
            e.printStackTrace();
        }

        return jArray;
    }
}
