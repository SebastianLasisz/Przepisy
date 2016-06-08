package com.pythonanywhere.sedi.foodster.models;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;


public class JSONfunctions {

    public static ResponseWrapper postWithJSONResult(String stringURL, String post_message) {

        HttpURLConnection connection = null;
        ResponseWrapper response = null;
        int responseCode = 0;
        String stringJSON = null;

        try {
            // Network access
            connection = (HttpURLConnection) new URL(stringURL).openConnection();
            connection.setUseCaches(false);
            connection.setDoOutput(true);
            connection.setDoInput(true);

            DataOutputStream wr = new DataOutputStream(connection.getOutputStream());
            wr.writeBytes(post_message);

            responseCode = connection.getResponseCode();
            if(responseCode == 200) {
                stringJSON = readInput(connection);
            }
            response = new ResponseWrapper(responseCode, stringJSON);

            if(wr != null) wr.close();
            connection.disconnect();

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return response;
    }

    public static ResponseWrapper getWithJSONResult(String stringURL, String token) {

        HttpURLConnection connection = null;
        ResponseWrapper response = null;
        int responseCode = 0;
        String stringJSON = null;

        System.out.println(token);

        try {
            // Network access
            connection = (HttpURLConnection) (new URL(stringURL)).openConnection();
            connection.addRequestProperty("Authorization", "Token " + token);

            responseCode = connection.getResponseCode();
            if(responseCode == 200) {
                stringJSON = readInput(connection);
            }
            response = new ResponseWrapper(responseCode, stringJSON);

            connection.disconnect();

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return response;
    }

    public static int restPut(String stringURL, String JSONAsString) {

        HttpURLConnection connection = null;
        ResponseWrapper response = null;
        int responseCode = 0;
        String stringJSON = null;

        try {
            // Network access
            connection = (HttpURLConnection) new URL(stringURL).openConnection();
            connection.setUseCaches(false);
            connection.setDoOutput(true);
            connection.setRequestMethod("PUT");

            DataOutputStream wr = new DataOutputStream(connection.getOutputStream());
            wr.writeBytes(JSONAsString);

            responseCode = connection.getResponseCode();
            if(wr != null) wr.close();
            connection.disconnect();

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return responseCode;
    }

    public static int restDelete(String stringURL, int itemID) {

        HttpURLConnection connection = null;
        ResponseWrapper response = null;
        int responseCode = 0;
        String stringJSON = null;

        try {
            // Network access
            connection = (HttpURLConnection) new URL(stringURL+itemID).openConnection();
            connection.setUseCaches(false);
            connection.setRequestMethod("DELETE");

            responseCode = connection.getResponseCode();
            response = new ResponseWrapper(responseCode, stringJSON);
            connection.disconnect();

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return responseCode;
    }

    private static String readInput(HttpURLConnection connection) throws IOException {

        InputStream in = new BufferedInputStream(connection.getInputStream());
        BufferedReader br = new BufferedReader(new InputStreamReader(in));
        StringBuilder stringBuilder = new StringBuilder();
        String line;

        while ((line = br.readLine()) != null) {
            stringBuilder.append(line).append('\n');
        }

        br.close();
        return stringBuilder.toString();
    }




}
