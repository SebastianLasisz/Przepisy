package com.pythonanywhere.sedi.foodster.fragments;

import android.content.Context;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

import com.pythonanywhere.sedi.foodster.R;
import com.pythonanywhere.sedi.foodster.models.JSONfunctions;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

public class ShoppingListFragment extends Fragment {

    private Spinner listSpinner;
    JSONArray jsonArray;
    ArrayList<String> nameList;

    public ShoppingListFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        updateSpinner();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_shopping_list, container, false);
    }

    public void updateSpinner(){

        new DownloadJSON().execute();
    }

    private class DownloadJSON extends AsyncTask<Void, Void, Void> {

        @Override
        protected Void doInBackground(Void... params) {

            nameList = new ArrayList<String>();

            jsonArray = JSONfunctions.getJSONfromURL(getResources().getString(R.string.shopping_list_list));
            JSONObject shoppingList;

            try {

                for (int i = 0; i < jsonArray.length(); i++) {
                    shoppingList = jsonArray.getJSONObject(i);

                    nameList.add(shoppingList.getString("name"));
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void args){

            listSpinner = (Spinner) getActivity().findViewById(R.id.spinner);
            listSpinner.setAdapter(new ArrayAdapter<String>(getActivity(),
                    android.R.layout.simple_spinner_item, nameList));


        }
    }
}
