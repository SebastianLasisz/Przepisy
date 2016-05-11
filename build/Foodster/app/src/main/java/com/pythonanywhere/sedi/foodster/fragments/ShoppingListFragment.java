package com.pythonanywhere.sedi.foodster.fragments;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

import com.pythonanywhere.sedi.foodster.R;
import com.pythonanywhere.sedi.foodster.models.JSONfunctions;
import com.pythonanywhere.sedi.foodster.models.ResponseWrapper;
import com.pythonanywhere.sedi.foodster.models.ShoppingList;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class ShoppingListFragment extends Fragment {

    private static Spinner listSpinner;
    private static JSONArray jsonArray;

    private static String token;
    private static List<String> nameList;
    private static List<ShoppingList> shoppingListsList;

    public ShoppingListFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        SharedPreferences sharedPref
                = getActivity().getSharedPreferences(getString(R.string.token_file_key), Context.MODE_PRIVATE);
        token = sharedPref.getString(getString(R.string.saved_token), "");

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
            shoppingListsList = new ArrayList<ShoppingList>();

            ResponseWrapper response = JSONfunctions.getWithJSONResult(getResources().getString(R.string.shopping_list_list), token);
            System.out.println(response.getResponseCode());

            if(response.getResponseCode() == 200) {

                try {

                    jsonArray = response.getJSONArray();
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                JSONObject shoppingList;
                ShoppingList sl;
                JSONArray items;

                try {

                    for (int i = 0; i < jsonArray.length(); i++) {
                        shoppingList = jsonArray.getJSONObject(i);

                        nameList.add(shoppingList.getString("name"));
                        sl = new ShoppingList(shoppingList.getString("name"),
                                shoppingList.getString("description"));

                        items = shoppingList.getJSONArray("items");
                        for (int j = 0; j < items.length(); j++) sl.addItem(items.getString(j));

                        shoppingListsList.add(sl);


                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void args){
            listSpinner = (Spinner) getActivity().findViewById(R.id.spinner);
            listSpinner.setAdapter(new ArrayAdapter<String>(getActivity(),
                    android.R.layout.simple_spinner_item, nameList));

            listSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
                @Override
                public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                    if(shoppingListsList.get(position) != null) {
                        ShoppingItemsFragment itemFragment = new ShoppingItemsFragment();
                        itemFragment.setShoppingList(shoppingListsList.get(position));
                        FragmentTransaction transaction = getChildFragmentManager().beginTransaction();
                        transaction.add(R.id.child_fragment, itemFragment).commit();
                    }
                }

                @Override
                public void onNothingSelected(AdapterView<?> parent) {

                }

            });
        }
    }
}
